// Configuración central de la API — CTech Backend (FastAPI)

export const API_CONFIG = {
    BASE_URL: 'http://localhost:8000',
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
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;
    return `${API_CONFIG.BASE_URL}${API_CONFIG.API_VERSION}/${cleanEndpoint}`;
}

// Petición autenticada genérica
export async function authenticatedRequest(url, options = {}) {
    const token = sessionStorage.getItem('authToken');

    const headers = {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options.headers,
    };

    const response = await fetch(url, { ...options, headers });

    if (response.status === 401) {
        sessionStorage.removeItem('authToken');
        sessionStorage.removeItem('user');
        window.location.href = '/';
        return null;
    }

    return response;
}

// Parsea la respuesta y lanza error si no es ok
export async function handleApiResponse(response) {
    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Error desconocido' }));
        throw new Error(error.detail || `Error ${response.status}: ${response.statusText}`);
    }
    return response.json();
}
