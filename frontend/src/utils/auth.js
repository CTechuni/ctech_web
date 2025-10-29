// Utilidades para manejo de autenticación
// TODO: Integrar con tu backend cuando esté listo

export class AuthManager {
    constructor() {
        this.tokenKey = 'authToken';
        this.userKey = 'user';
    }

    // Verificar si el usuario está autenticado
    isAuthenticated() {
        const token = this.getToken();
        return !!token && !this.isTokenExpired(token);
    }

    // Obtener token del localStorage
    getToken() {
        return localStorage.getItem(this.tokenKey);
    }

    // Obtener datos del usuario
    getUser() {
        const userStr = localStorage.getItem(this.userKey);
        return userStr ? JSON.parse(userStr) : null;
    }

    // Guardar datos de autenticación
    setAuthData(token, user) {
        localStorage.setItem(this.tokenKey, token);
        localStorage.setItem(this.userKey, JSON.stringify(user));
    }

    // Limpiar datos de autenticación
    clearAuthData() {
        localStorage.removeItem(this.tokenKey);
        localStorage.removeItem(this.userKey);
    }

    // Verificar si el token ha expirado (básico)
    isTokenExpired(token) {
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            const currentTime = Date.now() / 1000;
            return payload.exp < currentTime;
        } catch (error) {
            return true; // Si no se puede decodificar, considerarlo expirado
        }
    }

    // Login (simulado por ahora)
    async login(email, password, remember = false) {
        // TODO: Reemplazar con llamada real al backend
        // const response = await fetch('/api/auth/login', {
        //     method: 'POST',
        //     headers: { 'Content-Type': 'application/json' },
        //     body: JSON.stringify({ email, password, remember })
        // });
        
        // if (!response.ok) {
        //     throw new Error('Credenciales inválidas');
        // }
        
        // const data = await response.json();
        // this.setAuthData(data.token, data.user);
        // return data;

        // SIMULACIÓN TEMPORAL
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        if (email === 'test@example.com' && password === 'password') {
            const mockUser = {
                id: 1,
                email: email,
                name: 'Usuario de Prueba',
                role: 'user'
            };
            
            const mockToken = 'mock-jwt-token-' + Date.now();
            this.setAuthData(mockToken, mockUser);
            
            return { token: mockToken, user: mockUser };
        } else {
            throw new Error('Credenciales inválidas');
        }
    }

    // Logout
    async logout() {
        // TODO: Llamar al endpoint de logout del backend
        // await fetch('/api/auth/logout', {
        //     method: 'POST',
        //     headers: { 'Authorization': `Bearer ${this.getToken()}` }
        // });
        
        this.clearAuthData();
    }

    // Registro (simulado por ahora)
    async register(userData) {
        // TODO: Reemplazar con llamada real al backend
        // const response = await fetch('/api/auth/register', {
        //     method: 'POST',
        //     headers: { 'Content-Type': 'application/json' },
        //     body: JSON.stringify(userData)
        // });
        
        // if (!response.ok) {
        //     const error = await response.json();
        //     throw new Error(error.message);
        // }
        
        // return response.json();

        // SIMULACIÓN TEMPORAL
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // Validaciones simuladas
        if (!userData.community) {
            throw new Error('Debes seleccionar una comunidad');
        }
        
        if (!userData.inviteCode) {
            throw new Error('El código de invitación es requerido');
        }
        
        if (userData.inviteCode.length < 6) {
            throw new Error('El código de invitación debe tener al menos 6 caracteres');
        }
        
        console.log('Datos de registro:', userData);
        return { 
            message: 'Usuario registrado exitosamente',
            user: {
                id: Date.now(),
                email: userData.email,
                fullName: userData.fullName,
                community: userData.community
            }
        };
    }
    
    // Verificar código de invitación (simulado por ahora)
    async verifyInviteCode(code, community) {
        // TODO: Implementar verificación real con backend
        // const response = await fetch('/api/auth/verify-invite-code', {
        //     method: 'POST',
        //     headers: { 'Content-Type': 'application/json' },
        //     body: JSON.stringify({ code, community })
        // });
        
        // return response.json();

        // SIMULACIÓN TEMPORAL
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Códigos de prueba
        const validCodes = ['CTECH2024', 'WELCOME', 'COMMUNITY', 'DEVELOPER'];
        
        if (validCodes.includes(code.toUpperCase())) {
            return { valid: true, message: 'Código válido' };
        } else {
            throw new Error('Código de invitación inválido');
        }
    }
}

// Instancia global del AuthManager
export const authManager = new AuthManager();

// Función helper para verificar autenticación en componentes
export function requireAuth() {
    if (!authManager.isAuthenticated()) {
        // Redirigir al login o mostrar modal
        window.openModal('loginModal');
        return false;
    }
    return true;
}
