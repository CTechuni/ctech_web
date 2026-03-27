// frontend/src/utils/auth.js
import { API_CONFIG, buildApiUrl } from '../config/api.js';

// CAMBIO ESTRATÉGICO: Usamos localStorage para que el ADMIN no pierda la sesión al abrir pestañas de gestión.
const TOKEN_KEY = 'authToken';
const USER_KEY = 'user';

export class AuthManager {
    constructor() {
        this.authChangeListeners = [];
    }

    // ── Event listeners ───────────────────────────────────────────────────────
    onAuthChange(callback) {
        this.authChangeListeners.push(callback);
    }

    notifyAuthChange(action, user = null) {
        this.authChangeListeners.forEach(cb => {
            try { cb({ action, user }); } catch (e) { /* silencioso */ }
        });
    }

    // ── Estado ────────────────────────────────────────────────────────────────
    isAuthenticated() {
        const token = this.getToken();
        return !!token && !this.isTokenExpired(token);
    }

    getToken() {
        // CORRECCIÓN: Fix typo 'uandefined' -> 'undefined' y chequeo de window para SSR
        if (typeof window === 'undefined' || typeof localStorage === 'undefined') return null;
        return localStorage.getItem(TOKEN_KEY);
    }

    getUser() {
        if (typeof window === 'undefined' || typeof localStorage === 'undefined') return null;
        try {
            const raw = localStorage.getItem(USER_KEY);
            return raw ? JSON.parse(raw) : null;
        } catch {
            return null;
        }
    }

    // ── Persistencia ──────────────────────────────────────────────────────────
    setAuthData(token, user) {
        localStorage.setItem(TOKEN_KEY, token);
        localStorage.setItem(USER_KEY, JSON.stringify(user));
        this.notifyAuthChange('login', user);
    }

    clearAuthData() {
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(USER_KEY);
        this.notifyAuthChange('logout');
    }

    // ── Token (JWT Decoding) ──────────────────────────────────────────────────
    isTokenExpired(token) {
        try {
            if (!token) return true;
            const base64url = token.split('.')[1];
            const base64 = base64url.replace(/-/g, '+').replace(/_/g, '/');
            const padded = base64.padEnd(base64.length + (4 - base64.length % 4) % 4, '=');
            const payload = JSON.parse(atob(padded));
            
            // Margen de seguridad de 10 segundos
            return payload.exp ? (payload.exp - 10) < Date.now() / 1000 : false;
        } catch {
            return true;
        }
    }

    getCurrentContext() {
        if (typeof window === 'undefined') return { role: null };
        const path = window.location.pathname;
        if (path.startsWith('/admin')) return { role: 'admin' };
        if (path.startsWith('/leader')) return { role: 'leader' };
        if (path.startsWith('/user')) return { role: 'user' };
        return { role: null };
    }

    // ── Auth actions ──────────────────────────────────────────────────────────
    async login(email, password) {
        // CORRECCIÓN: Centralizamos el login usando el método estático fetch para heredar la lógica de errores
        const data = await AuthManager.fetch(API_CONFIG.AUTH.LOGIN, {
            method: 'POST',
            body: JSON.stringify({ email, password }),
        });

        if (data && data.access_token) {
            this.setAuthData(data.access_token, data.user);
        }
        return data;
    }

    async register(userData) {
        const payload = {
            email: userData.email,
            password: userData.password,
            name_user: userData.fullName || userData.name_user,
            community_id: parseInt(userData.community_id),
            invite_code: userData.inviteCode || userData.invite_code,
            rol_id: userData.rol_id || 4
        };
        return AuthManager.fetch(API_CONFIG.AUTH.REGISTER, {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    }

    async logout(reason = '') {
        const token = this.getToken();
        if (token) {
            try {
                // Notificamos al backend el cierre de sesión
                await fetch(buildApiUrl(API_CONFIG.AUTH.LOGOUT), {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${token}` }
                });
            } catch (e) { console.warn('Logout backend failed', e); }
        }
        this.clearAuthData();
        window.location.href = reason === 'inactivity' ? '/?reason=inactivity' : '/';
    }

    initInactivityTimer(timeoutMinutes = 120) {
        if (typeof window === 'undefined') return;
        let timeout;
        const ms = timeoutMinutes * 60 * 1000;
        const resetTimer = () => {
            clearTimeout(timeout);
            timeout = setTimeout(() => this.logout('inactivity'), ms);
        };
        ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart']
            .forEach(name => document.addEventListener(name, resetTimer, true));
        resetTimer();
    }

    // ── Peticiones autenticadas (CORREGIDO PARA SOPORTAR FORM-DATA Y NGORK) ──────────────────
static async fetch(endpoint, options = {}) {
    const token = typeof window !== 'undefined' ? localStorage.getItem(TOKEN_KEY) : null;
    
    const url = buildApiUrl(endpoint);

    console.log("🚀 Disparando a:", url);

    // 1. Manejo inteligente de Headers
    const headers = { ...options.headers };

    // CORRECCIÓN CLAVE: Solo añadimos JSON si el body NO es un FormData
    // Si es FormData (como el logo de la comunidad), el navegador DEBE poner el boundary
    if (!(options.body instanceof FormData)) {
        headers['Content-Type'] = headers['Content-Type'] || 'application/json';
    }

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    try {
        const response = await fetch(url, { ...options, headers });

        if (response.status === 401) {
            if (typeof window !== 'undefined') {
                localStorage.removeItem(TOKEN_KEY);
                localStorage.removeItem(USER_KEY);
                window.location.href = '/';
            }
            throw new Error('Sesión expirada.');
        }

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            const detail = Array.isArray(error.detail)
                ? error.detail.map(e => e.msg).join(', ')
                : (error.detail || `Error ${response.status}`);
            throw new Error(detail);
        }

        if (response.status === 204) return null;
        
        // Verificar si la respuesta es JSON antes de parsear
        const contentType = response.headers.get("content-type");
        if (contentType && contentType.includes("application/json")) {
            return response.json();
        }
        return response;
    } catch (error) {
        // ERROR DE RED: El servidor está caído o hay problemas de CORS
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            console.warn(`⚠️ Error de conexión con el servidor en [${endpoint}]. El backend no responde.`);
            // IMPORTANTE: No lanzamos el error o no dejamos que limpie la sesión aquí
            throw new Error('Servidor no disponible. Revisa tu conexión o el backend.');
        }

        console.error(`Error en API [${endpoint}]:`, error.message);
        throw error;
    }
}

}

export const authManager = new AuthManager();

// ── Guards mejorados para el Administrador ────────────────────────────────────

export function requireRole(expectedRole) {
    if (typeof window === 'undefined') return true;

    const user = authManager.getUser();
    
    // 1. Verificación básica
    if (!authManager.isAuthenticated() || !user) {
        window.location.href = '/';
        return false;
    }

    const normalize = (r) => String(r || '').toLowerCase().trim();
    const userRole = normalize(user.role || user.role_name || '');
    const targetRole = normalize(expectedRole);

    // 2. Si es ADMIN, entra a donde sea
    if (user.rol_id === 1 || userRole === 'admin') return true;

    // 3. LOGICA FLEXIBLE (Acepta inglés o español)
    const isUser = (r) => r === 'user' || r === 'usuario';
    const isLeader = (r) => r === 'leader' || r === 'lider';

    if (isUser(targetRole) && (isUser(userRole) || user.rol_id === 4)) {
        return true;
    }

    if (isLeader(targetRole) && (isLeader(userRole) || user.rol_id === 2)) {
        return true;
    }

    // 4. Comparación directa por si acaso
    if (userRole === targetRole) return true;

    // Si llegó aquí, es que realmente no tiene permiso
    console.warn(`⛔ Bloqueo: Esperaba '${targetRole}', pero el usuario tiene '${userRole}'`);
    window.location.href = '/';
    return false;
}