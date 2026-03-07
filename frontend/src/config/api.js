// Configuración de API para el backend
// TODO: Actualizar estas URLs cuando tengas tu backend listo

export const API_CONFIG = {
    // URLs base
    BASE_URL: 'http://localhost:8000', // Cambiar por tu URL de backend
    API_VERSION: '/api/v1',

    // Endpoints de autenticación
    AUTH: {
        LOGIN: '/auth/login',
        REGISTER: '/auth/register',
        LOGOUT: '/auth/logout',
        REFRESH: '/auth/refresh',
        FORGOT_PASSWORD: '/auth/forgot-password',
        RESET_PASSWORD: '/auth/reset-password',
        VERIFY_EMAIL: '/auth/verify-email',
        VERIFY_INVITE_CODE: '/auth/verify-invite-code'
    },

    // Endpoints de usuario
    USER: {
        PROFILE: '/user/profile',
        UPDATE_PROFILE: '/user/profile',
        CHANGE_PASSWORD: '/user/change-password',
        DELETE_ACCOUNT: '/user/delete'
    },

    // Endpoints de contenido
    CONTENT: {
        SEARCH: '/content/search',
        CATEGORIES: '/content/categories',
        ARTICLES: '/content/articles',
        TUTORIALS: '/content/tutorials'
    },

    // Endpoints de comunidades
    COMMUNITIES: {
        LIST: '/communities',
        JOIN: '/communities/join',
        LEAVE: '/communities/leave',
        CREATE: '/communities/create',
        GET_BY_ID: '/communities/:id',
        GET_MEMBERS: '/communities/:id/members'
    },

    // Endpoints del foro
    FORUM: {
        POSTS: '/forum/posts',
        CREATE_POST: '/forum/posts',
        COMMENTS: '/forum/comments',
        CATEGORIES: '/forum/categories'
    }
};

// Función helper para construir URLs completas
export function buildApiUrl(endpoint) {
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;
    const cleanVersion = API_CONFIG.API_VERSION.endsWith('/') ? API_CONFIG.API_VERSION : `${API_CONFIG.API_VERSION}/`;
    return `${API_CONFIG.BASE_URL}${cleanVersion}${cleanEndpoint}`;
}

// Función helper para hacer requests autenticados
export async function authenticatedRequest(url, options = {}) {
    const token = localStorage.getItem('authToken'); // ✅ Consistente con AuthManager

    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` })
        }
    };

    const finalOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers
        }
    };

    const response = await fetch(url, finalOptions);

    // Handle 401 Unauthorized
    if (response.status === 401) {
        localStorage.removeItem('authToken');
        localStorage.removeItem('user');
        localStorage.removeItem('lastAuthToken');
        window.location.href = '/';
        return null;
    }

    return response;
}

// Función para manejar respuestas de la API
export async function handleApiResponse(response) {
    if (!response.ok) {
        const error = await response.json().catch(() => ({ message: 'Error desconocido' }));
        throw new Error(error.message || `Error ${response.status}: ${response.statusText}`);
    }

    return response.json();
}
