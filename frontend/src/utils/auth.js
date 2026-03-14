// Utilidades para manejo de autenticación
import { API_CONFIG, buildApiUrl } from '../config/api.js';

// ── Claves en sessionStorage (aisladas por pestaña) ───────────────────────────
// sessionStorage nunca se comparte entre pestañas del mismo dominio,
// lo que permite tener 4 roles distintos abiertos simultáneamente.
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
            try { cb({ action, user }); } catch (e) { /* silently fail */ }
        });
    }

    // ── Estado ────────────────────────────────────────────────────────────────

    isAuthenticated() {
        const token = this.getToken();
        return !!token && !this.isTokenExpired(token);
    }

    getToken() {
        if (typeof sessionStorage === 'undefined') return null;
        return sessionStorage.getItem(TOKEN_KEY);
    }

    getUser() {
        if (typeof sessionStorage === 'undefined') return null;
        try {
            const raw = sessionStorage.getItem(USER_KEY);
            return raw ? JSON.parse(raw) : null;
        } catch {
            return null;
        }
    }

    // ── Persistencia ──────────────────────────────────────────────────────────

    setAuthData(token, user) {
        sessionStorage.setItem(TOKEN_KEY, token);
        sessionStorage.setItem(USER_KEY, JSON.stringify(user));
        this.notifyAuthChange('login', user);
    }

    clearAuthData() {
        sessionStorage.removeItem(TOKEN_KEY);
        sessionStorage.removeItem(USER_KEY);
        this.notifyAuthChange('logout');
    }

    // ── Token ─────────────────────────────────────────────────────────────────

    isTokenExpired(token) {
        try {
            // JWT usa base64URL (- y _ en lugar de + y /, sin padding =)
            // atob() solo acepta base64 estándar, hay que convertir primero
            const base64url = token.split('.')[1];
            const base64 = base64url.replace(/-/g, '+').replace(/_/g, '/');
            const padded = base64.padEnd(base64.length + (4 - base64.length % 4) % 4, '=');
            const payload = JSON.parse(atob(padded));
            return payload.exp ? payload.exp < Date.now() / 1000 : false;
        } catch {
            return true;
        }
    }

    // ── Contexto de URL (para requireRole) ────────────────────────────────────

    getCurrentContext() {
        if (typeof window === 'undefined') return { role: null };
        const path = window.location.pathname;
        let role = null;
        if (path.startsWith('/admin')) role = 'admin';
        else if (path.startsWith('/leader')) role = 'leader';
        else if (path.startsWith('/user')) role = 'user';
        return { role };
    }

    // ── Auth actions ──────────────────────────────────────────────────────────

    async login(email, password) {
        const url = buildApiUrl(API_CONFIG.AUTH.LOGIN);
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password }),
            });

            if (!response.ok) {
                const err = await response.json().catch(() => ({}));
                const detail = Array.isArray(err.detail)
                    ? err.detail.map(e => e.msg).join(', ')
                    : (err.detail || 'Credenciales inválidas');
                throw new Error(detail);
            }

            const data = await response.json();
            // sessionStorage ya es aislada por pestaña; solo guardamos la nueva sesión
            this.setAuthData(data.access_token, data.user);
            return data;
        } catch (error) {
            throw error;
        }
    }

    async register(userData) {
        const payload = {
            email: userData.email,
            password: userData.password,
            name_user: userData.fullName || userData.name_user,
            community_id: parseInt(userData.community_id || userData.community),
            invite_code: userData.inviteCode || userData.invite_code,
            rol_id: userData.rol_id || 4
        };
        return AuthManager.fetch(API_CONFIG.AUTH.REGISTER, {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    }

<<<<<<< HEAD
    async logout(reason = '') {
        const token = this.getToken();
        if (token) {
            try {
                await fetch(buildApiUrl(API_CONFIG.AUTH.LOGOUT), {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${token}` }
                });
            } catch { /* silencioso — igual limpiamos la sesión local */ }
        }
=======
    logout(reason = '') {
>>>>>>> origin/main
        this.clearAuthData();
        window.location.href = reason === 'inactivity' ? '/?reason=inactivity' : '/';
    }

    // ── Timer de Inactividad ──────────────────────────────────────────────────

    initInactivityTimer(timeoutMinutes = 120) {
        if (typeof window === 'undefined') return;
        let timeout;
        const ms = timeoutMinutes * 60 * 1000;
        const resetTimer = () => {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                console.warn('Sesión cerrada por inactividad');
                this.logout('inactivity');
            }, ms);
        };
        ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart']
            .forEach(name => document.addEventListener(name, resetTimer, true));
        resetTimer();
    }

    // ── Peticiones autenticadas (estático) ────────────────────────────────────

    static async fetch(endpoint, options = {}) {
        const token = sessionStorage.getItem(TOKEN_KEY);
        const url = buildApiUrl(endpoint);

        const headers = { ...options.headers };
        if (!(options.body instanceof FormData)) {
            headers['Content-Type'] = headers['Content-Type'] || 'application/json';
        }
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        try {
            const response = await fetch(url, { ...options, headers });

            if (response.status === 401) {
                throw new Error('Sesión expirada o sin permisos (401).');
            }
            if (!response.ok) {
                const error = await response.json().catch(() => ({}));
                const detail = Array.isArray(error.detail)
                    ? error.detail.map(e => e.msg).join(', ')
                    : (error.detail || `Error ${response.status}`);
                throw new Error(detail);
            }

            const contentType = response.headers.get('content-type') || '';
            if (response.status === 204 || !contentType.includes('application/json')) return null;

            return response.json();
        } catch (error) {
            console.error(`AuthManager.fetch FAILED [${url}]:`, error);
            throw error;
        }
    }
}

// ── Instancia global ──────────────────────────────────────────────────────────

export const authManager = new AuthManager();

// ── Guards ────────────────────────────────────────────────────────────────────

export function requireAuth() {
    if (typeof window === 'undefined') return true;
    if (!authManager.isAuthenticated()) {
        window.location.href = '/';
        return false;
    }
    return true;
}

export function requireRole(expectedRole) {
    if (typeof window === 'undefined') return true;

    const token = authManager.getToken();
    if (!token || authManager.isTokenExpired(token)) {
        window.location.href = '/';
        return false;
    }

    const { role: pathRole } = authManager.getCurrentContext();
    const user = authManager.getUser();

    const normalize = (r) => {
        if (!r) return '';
        const nr = String(r).toLowerCase().trim();
        if (nr.includes('admin')) return 'admin';
        if (nr.includes('leader') || nr.includes('lider')) return 'leader';
        if (nr === 'user' || nr === 'usuario' || nr === 'standard') return 'usuario';
        return nr;
    };

    const userRole = normalize(user?.role || pathRole || '');
    const targetRole = normalize(expectedRole);

    if (userRole === targetRole) return true;
    if (normalize(pathRole) === targetRole) return true;

    console.warn('[Auth] Acceso denegado.', { userRole, targetRole });
    window.location.href = '/';
    return false;
}

export function onAuthStateChanged(callback) {
    authManager.onAuthChange(callback);
}
