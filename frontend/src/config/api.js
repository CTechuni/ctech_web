// Configuración central de la API — CTech Backend (FastAPI)

export const API_CONFIG = {
    BASE_URL: 'http://localhost:8000',
    API_VERSION: '/api/v1',

    AUTH: {
        LOGIN:           '/auth/login',
        REGISTER:        '/auth/register',
        LOGOUT:          '/auth/logout',
        FORGOT_PASSWORD: '/auth/forgot-password',
        RESET_PASSWORD:  '/auth/reset-password',
    },

    USERS: {
        ME:              '/users/me',
        CHANGE_PASSWORD: '/users/me/password',
        LIST:            '/users/',             // ?page=1&limit=6&role=all&search=
        LEADERS:         '/users/leaders',
        MENTORS:         '/users/mentors',
        BY_COMMUNITY:    '/users/community/',   // + community_id
        UPDATE:          '/users/',             // + user_id  PATCH
        DELETE:          '/users/',             // + user_id  DELETE
        PROMOTE:         '/users/',             // + user_id + /promote  PATCH
        DEMOTE:          '/users/',             // + user_id + /demote   PATCH
    },

    COMMUNITIES: {
        PUBLIC:          '/communities/public',
        WITH_LOGO:       '/communities/with-logo',
        LIST:            '/communities/',
        CREATE:          '/communities/',
        UPDATE:          '/communities/',       // + id  PATCH
        DELETE:          '/communities/',       // + id  DELETE
        UPLOAD_LOGO:     '/communities/upload',
    },

    EVENTS: {
        LIST:            '/events/',            // GET — sin auth: aprobados+públicos; auth: aprobados; líder: su comunidad; admin: todos
        MY:              '/events/my',          // GET — solo mentor: sus propios eventos (todos estados)
        PENDING:         '/events/pending',     // GET — líder: pendientes de su comunidad
        UPCOMING:        '/events/upcoming',
        CREATE:          '/events/',            // POST — admin(1), líder(3), mentor(2)
        UPDATE:          '/events/',            // + event_id  PUT
        APPROVE:         '/events/',            // + event_id + /approve  PATCH (líder/admin)
        REJECT:          '/events/',            // + event_id + /reject   PATCH (líder/admin)
        REGISTER:        '/events/',            // + event_id + /register  POST
        DELETE:          '/events/',            // + event_id  DELETE
    },

    COURSES: {
        LIST:            '/courses/',           // solo aprobados (público)
        PENDING:         '/courses/pending',    // líder y admin
        ALL:             '/courses/all',        // solo admin
        DETAIL:          '/courses/',           // + id  GET
        CREATE:          '/courses/',           // solo mentor
        UPDATE:          '/courses/',           // + id  PUT (solo mentor dueño)
        DELETE:          '/courses/',           // + id  DELETE (mentor dueño o admin)
        APPROVE:         '/courses/',           // + id + /approve  PATCH (líder/admin)
        REJECT:          '/courses/',           // + id + /reject   PATCH (líder/admin)
    },

    METRICS: {
        ADMIN:           '/metrics/admin',
        MENTOR:          '/metrics/mentor',
        COMMUNITY:       '/metrics/community/', // + community_id
    },

    NOTIFICATIONS: {
        LIST:            '/notifications/',
        MARK_READ:       '/notifications/',     // + id + /read  PATCH
        MARK_ALL_READ:   '/notifications/read-all',
    },

    CONTENT: {
        LIST:            '/contenido/',
        DETAIL:          '/contenido/',         // + content_id
        CREATE:          '/contenido/',         // admin o mentor
        UPDATE:          '/contenido/',         // + content_id  PUT
        DELETE:          '/contenido/',         // + content_id  DELETE
    },

    SPECIALTIES: {
        LIST:            '/specialties/',
        CREATE:          '/specialties/',       // solo admin
    },

    TECHNOLOGIES: {
        LIST:            '/technologies/',
        CREATE:          '/technologies/',      // admin o líder
    },

    SESSIONS: {
        CREATE:          '/sessions/',
        BY_COURSE:       '/sessions/course/',   // + course_id
        RESERVE:         '/sessions/',          // + id + /reserve  POST
        CANCEL:          '/sessions/',          // + id + /cancel   DELETE
    },
};

// Construye la URL completa: BASE_URL + /api/v1 + endpoint
export function buildApiUrl(endpoint) {
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;
    return `${API_CONFIG.BASE_URL}${API_CONFIG.API_VERSION}/${cleanEndpoint}`;
}

// Petición autenticada genérica
export async function authenticatedRequest(url, options = {}) {
    const token = localStorage.getItem('authToken');

    const headers = {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options.headers,
    };

    const response = await fetch(url, { ...options, headers });

    if (response.status === 401) {
        localStorage.removeItem('authToken');
        localStorage.removeItem('user');
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
