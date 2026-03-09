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
        else if (path.startsWith('/user')) role = 'usuario';

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
        const expired = token ? this.isTokenExpired(token) : true;

        console.debug('[Auth] ¿Autenticado?:', {
            hasToken: !!token,
            isExpired: expired,
            role,
            id
        });

        return !!token && !expired;
    }

    getToken(role, id) {
        if (!role && !id) {
            const ctx = this.getCurrentContext();
            role = ctx.role;
            id = ctx.id;
        }

        // 1. Try context-specific key (if ID present)
        if (id) {
            const contextKey = this.getTokenKey(role, id);
            const contextToken = localStorage.getItem(contextKey);
            if (contextToken) return contextToken;
        }

        // 2. Special case for Admin
        if (String(role).toLowerCase() === 'admin') {
            const adminToken = localStorage.getItem('token_admin_001');
            if (adminToken) return adminToken;
        }

        // 3. Fallback to base key (authToken)
        return localStorage.getItem(this.baseTokenKey);
    }

    getUser(role, id) {
        if (!role && !id) {
            const ctx = this.getCurrentContext();
            role = ctx.role;
            id = ctx.id;
        }

        // 1. Try context-specific key (if ID present)
        if (id) {
            const contextKey = this.getUserKey(role, id);
            let raw = localStorage.getItem(contextKey);
            if (raw) try { return JSON.parse(raw); } catch (e) { }
        }

        // 2. Special case for Admin
        if (String(role).toLowerCase() === 'admin') {
            const rawAdmin = localStorage.getItem('user_admin_001');
            if (rawAdmin) try { return JSON.parse(rawAdmin); } catch (e) { }
        }

        // 3. Fallback to base key
        const raw = localStorage.getItem(this.baseUserKey);
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

    logout(reason = '') {
        const { role, id } = this.getCurrentContext();
        this.clearAuthData(role, id);

        let url = '/';
        if (reason === 'inactivity') {
            url = '/?reason=inactivity';
        }

        window.location.href = url;
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

        // Eventos que cuentan como "actividad"
        const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'];
        events.forEach(name => {
            document.addEventListener(name, resetTimer, true);
        });

        resetTimer(); // Iniciar
        console.log(`Timer de inactividad iniciado: ${timeoutMinutes} min`);
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

        try {
            const response = await fetch(url, { ...options, headers });

            if (response.status === 401) {
                throw new Error('Tu sesión ha expirado o no tienes permisos (401). El redirect está deshabilitado.');
            }

            if (!response.ok) {
                const error = await response.json().catch(() => ({}));
                throw new Error(error.detail || `Error ${response.status}`);
            }

            // Respuestas 204 No Content no tienen body
            const contentType = response.headers.get('content-type') || '';
            if (response.status === 204 || !contentType.includes('application/json')) return null;

            return response.json();
        } catch (error) {
            console.error(`DEBUG: AuthManager.fetch FAILED for ${url}:`, error);
            throw error;
        }
    }
}

// ── Instancia global y helpers ────────────────────────────────────────────────

export const authManager = new AuthManager();

/** Redirige al inicio si el usuario no está autenticado. */
export function requireAuth() {
    if (typeof window === 'undefined') return true;

    if (!authManager.isAuthenticated()) {
        console.warn('requireAuth: No autenticado, redirigiendo a /');
        window.location.href = '/';
        return false;
    }
    return true;
}

/** Redirige al inicio si el usuario no tiene el rol esperado. */
export function requireRole(expectedRole) {
    if (typeof window === 'undefined') return true;

    // 1. Verificar autenticación base
    const token = authManager.getToken();
    if (!token || authManager.isTokenExpired(token)) {
        console.warn('[Auth] No autenticado o token expirado. Redirigiendo...');
        window.location.href = '/';
        return false;
    }

    const { role: pathRole } = authManager.getCurrentContext();
    const user = authManager.getUser();

    // Normalización Flexible: permite variaciones en los nombres de roles
    const normalize = (r) => {
        if (!r) return '';
        const nr = String(r).toLowerCase().trim();
        if (nr.includes('mentor')) return 'mentor';
        if (nr.includes('admin')) return 'admin';
        if (nr.includes('leader') || nr.includes('lider')) return 'leader';
        if (nr === 'user' || nr === 'usuario' || nr === 'standard') return 'usuario';
        return nr;
    };

    const userRole = normalize(user?.role || pathRole || '');
    const targetRole = normalize(expectedRole);

    console.debug('[Auth] Control de Acceso:', {
        esperado: targetRole,
        detectado: userRole,
        pathRole: pathRole
    });

    // Si coinciden los roles normalizados, permitir acceso
    if (userRole === targetRole) return true;

    // Si el rol detectado por URL coincide con el esperado, dar el beneficio de la duda
    // (Útil si el objeto user no cargó correctamente pero el token es válido para esa ruta)
    if (normalize(pathRole) === targetRole) return true;

    console.warn('[Auth] ¡Acceso Denegado! Roles no coinciden.', {
        userRole, targetRole
    });

    window.location.href = '/';
    return false;
}

/**
 * Event listener para cambios de autenticación
 * Útil para sincronizar UI entre pestañas
 */
export function onAuthStateChanged(callback) {
    authManager.onAuthChange(callback);
}
