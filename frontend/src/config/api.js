// Configuración central de la API — CTech Backend (FastAPI)

export const API_CONFIG = {
    // CORRECCIÓN: Detectar automáticamente si estamos en producción (ngrok/nube) o local
    BASE_URL:"",
    
    API_VERSION: '/api/v1',

    AUTH: {
        LOGIN: '/auth/login',
        REGISTER: '/auth/register',
        LOGOUT: '/auth/logout',
        FORGOT_PASSWORD: '/auth/forgot-password',
        RESET_PASSWORD: '/auth/reset-password',
    },

    USERS: {
        ME: '/users/me',
        CHANGE_PASSWORD: '/users/me/password',
        LIST: '/users/',             // ?page=1&limit=6&role=all&search=
        LEADERS: '/users/leaders',
        BY_COMMUNITY: '/users/community/',   // + community_id
        UPDATE: '/users/',             // + user_id  PATCH
        DELETE: '/users/',             // + user_id  DELETE
        ROLE: '/users/',             // + user_id + /role  PATCH (solo admin)
    },

    COMMUNITIES: {
        PUBLIC: '/communities/public',
        WITH_LOGO: '/communities/with-logo',
        LIST: '/communities/',
        CREATE: '/communities/',
        UPDATE: '/communities/',       // + id  PATCH
        DELETE: '/communities/',       // + id  DELETE
        UPLOAD_LOGO: '/communities/upload',
    },

    EVENTS: {
        LIST: '/events/',            // GET — sin auth: aprobados+públicos; auth: aprobados; líder: su comunidad; admin: todos
        PENDING: '/events/pending',     // GET — líder: pendientes de su comunidad
        UPCOMING: '/events/upcoming',
        CREATE: '/events/',            // POST — admin(1), líder(3)
        UPDATE: '/events/',            // + event_id  PUT
        APPROVE: '/events/',            // + event_id + /approve  PATCH (líder/admin)
        REJECT: '/events/',            // + event_id + /reject   PATCH (líder/admin)
        REGISTER: '/events/',            // + event_id + /register  POST
        DELETE: '/events/',            // + event_id  DELETE
    },

    METRICS: {
        ADMIN: '/metrics/admin',
        COMMUNITY: '/metrics/community/', // + community_id
    },

    NOTIFICATIONS: {
        LIST: '/notifications/',
        MARK_READ: '/notifications/',     // + id + /read  PATCH
        MARK_ALL_READ: '/notifications/read-all',
    },

    CONTENT: {
        LIST: '/contenido/',
        DETAIL: '/contenido/',         // + content_id
        CREATE: '/contenido/',         // admin o mentor
        UPDATE: '/contenido/',         // + content_id  PUT
        DELETE: '/contenido/',         // + content_id  DELETE
    },

};

// Construye la URL completa: BASE_URL + /api/v1 + endpoint
export function buildApiUrl(endpoint) {
    // Si el endpoint ya es una URL completa, no hagas nada
    if (endpoint.startsWith('http')) return endpoint;
    
    // Si no, construye una ruta relativa
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
    
    // Esto devolverá algo como "/api/v1/users"
    return `${API_CONFIG.BASE_URL}${API_CONFIG.API_VERSION}${cleanEndpoint}`;
}

/**
 * Petición autenticada con manejo de estados y errores
 */
export async function authenticatedRequest(endpoint, options = {}) {
    const url = buildApiUrl(endpoint);
    const token = localStorage.getItem('authToken');

    // Seteamos headers por defecto
    const headers = {
        'ngrok-skip-browser-warning': '69420',
        'Accept': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options.headers,
    };

    // Si enviamos FormData (para logos/archivos), el navegador pone el Content-Type solo
    if (!(options.body instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
    }

    try {
        const response = await fetch(url, { ...options, headers });

        // MANEJO DE EXPIRACIÓN DE TOKEN (401)
        if (response.status === 401) {
            console.warn("Sesión expirada o no autorizada. Redirigiendo...");
            localStorage.clear(); // Limpiamos todo
            if (typeof window !== 'undefined') {
                // Evitamos loop de redirección si ya estamos en el login
                if (window.location.pathname !== '/') {
                    window.location.href = '/?expired=true';
                }
            }
            return null;
        }

        return response;
    } catch (error) {
        console.error('Error de red/túnel:', error);
        throw new Error('Error de conexión: El servidor no responde (¿Ngrok activo?)');
    }
}

/**
 * Procesa la respuesta de FastAPI y extrae los mensajes de error
 */
export async function handleApiResponse(response) {
    if (!response) return null;
    
    const data = await response.json().catch(() => ({ detail: 'Error en formato de respuesta' }));

    if (!response.ok) {
        // FastAPI suele enviar errores en 'detail'
        // Si es validación de Pydantic, 'detail' es una lista
        let message = 'Error en la operación';
        
        if (typeof data.detail === 'string') {
            message = data.detail;
        } else if (Array.isArray(data.detail)) {
            message = data.detail.map(err => `${err.loc[1]}: ${err.msg}`).join(' | ');
        }
        
        throw new Error(message);
    }
    
    return data;
}