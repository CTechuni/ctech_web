// Utilidades para manejo de autenticación
import { API_CONFIG, buildApiUrl } from '../config/api.js';

export class AuthManager {
    constructor() {
        this.baseTokenKey = 'authToken';
        this.baseUserKey = 'user';
        this.authChangeListeners = [];
        this.setupStorageListener();
    }

    // ── Helper: Dynamic Keys ──────────────────────────────────────────────────

    /**
     * Genera una clave única por rol e ID para soportar múltiples sesiones.
     */
    getTokenKey(role, id) {
        if (!role) return this.baseTokenKey;
        const r = String(role).toLowerCase();
        if (r === 'admin') return 'token_admin_001';
        return `token_${r}_${id}`;
    }

    getUserKey(role, id) {
        if (!role) return this.baseUserKey;
        const r = String(role).toLowerCase();
        if (r === 'admin') return 'user_admin_001';
        return `user_${r}_${id}`;
    }

    /**
     * Intenta determinar el rol e id actuales desde la URL o el estado global.
     */
    getCurrentContext() {
        if (typeof window === 'undefined') return { role: null, id: null };

        const path = window.location.pathname;
        const params = new URLSearchParams(window.location.search);

        let role = null;
        let id = params.get('id');

        if (path.startsWith('/admin')) role = 'admin';
        else if (path.startsWith('/mentor')) role = 'mentor';
        else if (path.startsWith('/leader')) role = 'leader';
        else if (path.startsWith('/user')) role = 'user';

        return { role, id };
    }

    // ── Setup: Sincronización entre pestañas ──────────────────────────────────

    setupStorageListener() {
        if (typeof window === 'undefined') return;

        window.addEventListener('storage', (event) => {
            // Sincronización básica para la sesión activa actual
            const { role, id } = this.getCurrentContext();
            const currentTokenKey = this.getTokenKey(role, id);

            if (event.key === currentTokenKey) {
                if (!event.newValue) {
                    this.handleRemoteLogout();
                } else {
                    this.handleRemoteLogin();
                }
            }
        });
    }

    handleRemoteLogout() {
        this.notifyAuthChange('logout');
    }

    handleRemoteLogin() {
        const { role, id } = this.getCurrentContext();
        const user = this.getUser(role, id);
        this.notifyAuthChange('login', user);
    }

    // ── Event listeners ────────────────────────────────────────────────────────

    onAuthChange(callback) {
        this.authChangeListeners.push(callback);
    }

    notifyAuthChange(action, user = null) {
        this.authChangeListeners.forEach(cb => {
            try { cb({ action, user }); }
            catch (e) { /* silently fail */ }
        });
    }

    // ── Estado ────────────────────────────────────────────────────────────────

    isAuthenticated(role, id) {
        const token = this.getToken(role, id);
        return !!token && !this.isTokenExpired(token);
    }

    getToken(role, id) {
        if (!role && !id) {
            const ctx = this.getCurrentContext();
            role = ctx.role;
            id = ctx.id;
        }
        return localStorage.getItem(this.getTokenKey(role, id));
    }

    getUser(role, id) {
        if (!role && !id) {
            const ctx = this.getCurrentContext();
            role = ctx.role;
            id = ctx.id;
        }
        const raw = localStorage.getItem(this.getUserKey(role, id));
        try { return raw ? JSON.parse(raw) : null; }
        catch { return null; }
    }

    // ── Persistencia ──────────────────────────────────────────────────────────

    setAuthData(token, user) {
        const role = user.role;
        const id = user.id;
        const tokenKey = this.getTokenKey(role, id);
        const userKey = this.getUserKey(role, id);

        localStorage.setItem(tokenKey, token);
        localStorage.setItem(userKey, JSON.stringify(user));

        // Mantener compatibilidad mínima o para "última sesión"
        localStorage.setItem(this.baseTokenKey, token);
        localStorage.setItem(this.baseUserKey, JSON.stringify(user));

        this.notifyAuthChange('login', user);
    }

    clearAuthData(role, id) {
        const tokenKey = this.getTokenKey(role, id);
        const userKey = this.getUserKey(role, id);

        localStorage.removeItem(tokenKey);
        localStorage.removeItem(userKey);

        // Si coincide con las base keys, limpiar también
        if (localStorage.getItem(this.baseTokenKey) === localStorage.getItem(tokenKey)) {
            localStorage.removeItem(this.baseTokenKey);
            localStorage.removeItem(this.baseUserKey);
        }

        this.notifyAuthChange('logout');
    }

    // ── Token ─────────────────────────────────────────────────────────────────

    isTokenExpired(token) {
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            return payload.exp ? payload.exp < Date.now() / 1000 : false;
        } catch {
            return true;
        }
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

                // Handle Pydantic array detail or string
                const detail = Array.isArray(err.detail)
                    ? err.detail.map(e => e.msg).join(', ')
                    : (err.detail || 'Credenciales inválidas');

                throw new Error(detail);
            }

            const data = await response.json();
            console.debug('authManager.login received', data);
            this.setAuthData(data.access_token, data.user);
            console.debug('authManager.login stored token, user', data.user);
            return data;
        } catch (error) {
            console.error('authManager.login error', error);
            throw error;
        }
    }

    async register(userData) {
        // Mapear los nombres de campo del formulario a los que espera el backend
        const payload = {
            email: userData.email,
            password: userData.password,
            name_user: userData.fullName || userData.name_user,
            community_id: parseInt(userData.community_id || userData.community),
            invite_code: userData.inviteCode || userData.invite_code,
            rol_id: userData.rol_id || 4 // Standard user por defecto
        };

        return AuthManager.fetch(API_CONFIG.AUTH.REGISTER, {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    }

    logout() {
        const { role, id } = this.getCurrentContext();
        this.clearAuthData(role, id);
        window.location.href = '/';
    }

    // ── Peticiones autenticadas (estático) ────────────────────────────────────

    /**
     * Realiza una petición autenticada al backend.
     * @param {string} endpoint  - Ruta relativa, ej: '/users/'
     * @param {RequestInit} options
     */
    static async fetch(endpoint, options = {}) {
        // Usar la instancia global para obtener el token dinámico
        const token = authManager.getToken();
        const url = buildApiUrl(endpoint);

        const headers = { ...options.headers };

        if (!(options.body instanceof FormData)) {
            headers['Content-Type'] = headers['Content-Type'] || 'application/json';
        }

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await fetch(url, { ...options, headers });

        if (response.status === 401) {
            /* ⚠️ BYPASS TEMPORAL - Redirect deshabilitado para simulacro visual.
            const { role, id } = authManager.getCurrentContext();
            authManager.clearAuthData(role, id);
            window.location.href = '/';
            */
            console.warn('[BYPASS VISUAL] 401 recibido en AuthManager.fetch - redirect deshabilitado.');
            return null;
        }

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || `Error ${response.status}`);
        }

        // Respuestas 204 No Content no tienen body
        const contentType = response.headers.get('content-type') || '';
        if (response.status === 204 || !contentType.includes('application/json')) return null;

        return response.json();
    }
}

// ── Instancia global y helpers ────────────────────────────────────────────────

export const authManager = new AuthManager();

/** Redirige al inicio si el usuario no está autenticado. */
export function requireAuth() {
    /**
     * IMPLEMENTACIÓN ORIGINAL (COMENTADA TEMPORALMENTE)
     *
     * if (!authManager.isAuthenticated()) {
     *     window.location.href = '/';
     *     return false;
     * }
     * return true;
     */

    // Autenticación deshabilitada para permitir navegar sin login
    return true;
}

/** Redirige al inicio si el usuario no tiene el rol esperado. */
export function requireRole(role) {
    /**
     * IMPLEMENTACIÓN ORIGINAL (COMENTADA TEMPORALMENTE)
     *
     * if (!requireAuth()) return false;
     * const userRole = authManager.getRole();
     * console.debug('requireRole check', role, 'currentRole', userRole);
     * if (!userRole.includes(role.toLowerCase())) {
     *     console.warn('requireRole failed, redirecting to /', userRole, role);
     *     window.location.href = '/';
     *     return false;
     * }
     * return true;
     */

    // Comprobación de rol deshabilitada para desarrollo
    return true;
}

/**
 * Event listener para cambios de autenticación
 * Útil para sincronizar UI entre pestañas
 */
export function onAuthStateChanged(callback) {
    authManager.onAuthChange(callback);
}
