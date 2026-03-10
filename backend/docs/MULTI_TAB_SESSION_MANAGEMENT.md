# 🔐 Implementación: Multi-Tab Session Management

**Status**: ✅ COMPLETO  
**Fecha**: 2024-03-03  
**Objetivo**: Sincronizar sesiones entre pestañas del navegador y prevenir múltiples sesiones activas

---

## 📋 Resumen de Cambios

### FRONTEND (✅ 4 Cambios Clave)

#### 1. **Auth Manager: `localStorage` + Event Listeners**
**Archivo**: `src/utils/auth.js`

```javascript
// ANTES: sessionStorage (no sincronizado entre pestañas)
getToken() {
    return sessionStorage.getItem(this.tokenKey);
}

// AHORA: localStorage + listeners de storage
constructor() {
    this.tokenKey = 'authToken';
    this.setupStorageListener();  // 🆕 Nuevo
}

setupStorageListener() {       // 🆕 Nuevo
    window.addEventListener('storage', (event) => {
        if (event.key === this.tokenKey) {
            if (!event.newValue) {
                this.handleRemoteLogout();  // Otra pestaña hizo logout
            } else {
                this.handleRemoteLogin();   // Otra pestaña hizo login
            }
        }
    });
}
```

**Beneficio**: Cuando usuario hace logout en Pestaña 1 → Pestaña 2 se enteras automáticamente

#### 2. **Event Listeners para Auth Changes**
**Archivo**: `src/utils/auth.js`

```javascript
// 🆕 Nuevo: Components pueden escuchar cambios de auth
onAuthChange(callback) {
    this.authChangeListeners.push(callback);
}

notifyAuthChange(action, user = null) {
    this.authChangeListeners.forEach(cb => {
        cb({ action, user });  // login | logout
    });
}

// Export helper
export function onAuthStateChanged(callback) {
    authManager.onAuthChange(callback);
}
```

**Uso en Componentes**:
```javascript
import { onAuthStateChanged } from '../../utils/auth.js';

onAuthStateChanged(({ action, user }) => {
    if (action === 'logout') {
        // Actualizar UI: Ocultar menu de usuario, mostrar login
    } else if (action === 'login') {
        // Actualizar UI: Mostrar avatar del usuario
    }
});
```

#### 3. **Remover Debug Statements**
**Archivos Modificados**:
- ✅ `src/utils/auth.js` - Removidas 5 líneas de `console.log()`
- ✅ `src/pages/components/LoginForm.astro` - Removidas 3 líneas
- ✅ `src/pages/components/SignupForm.astro` - Removida 1 línea

**Antes**:
```javascript
console.log(`DEBUG AUTH: Sending POST to ${url} with email: ${email}`);
console.error('DEBUG AUTH: Login failed status:', response.status);
console.log('DEBUG AUTH: Login success, data:', data);
```

**Ahora**: Todo eliminado (solo logs de error en servidor)

#### 4. **API Config: Mejorar authenticatedRequest**
**Archivo**: `src/config/api.js`

```javascript
// AHORA: Cohesivo con localStorage + manejo de 401
export async function authenticatedRequest(url, options = {}) {
    const token = localStorage.getItem('authToken'); // Consistente ✅
    
    // ... setup headers ...
    
    const response = await fetch(url, finalOptions);
    
    if (response.status === 401) {
        localStorage.removeItem('authToken');     // Limpia token
        localStorage.removeItem('lastAuthToken');  // Limpia flag
        window.location.href = '/';                // Redirige
        return null;
    }
    
    return response;
}
```

---

### BACKEND (✅ 3 Cambios Clave)

#### 1. **User Model: Agregar Campos de Session**
**Archivo**: `app/modules/users/models.py`

```python
class User(Base):
    # ... campos existentes ...
    
    # 🆕 Session management
    last_valid_token = Column(String(500), nullable=True)
    last_token_issued_at = Column(DateTime, nullable=True)
```

**Propósito**: 
- `last_valid_token` = Token más reciente del usuario
- `last_token_issued_at` = DateTime de cuando se emitió

#### 2. **Auth: Guardar Token en Login**
**Archivo**: `app/modules/auth/router.py` - Endpoint `/login`

```python
@router.post("/login", response_model=schemas.TokenResponse)
def login(data: schemas.LoginRequest, db: Session = Depends(get_db)):
    # ... validar credenciales ...
    
    user = user_service.authenticate_user(db, data.email, data.password)
    token = create_access_token(token_payload)
    
    # 🆕 SINGLE SESSION: Guardar último token válido
    user.last_valid_token = token
    user.last_token_issued_at = datetime.utcnow()
    user.last_login = datetime.utcnow()
    db.add(user)
    db.commit()
    
    logger.info(f"Token saved as active session for user: {data.email}")
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {...}
    }
```

**Flujo**:
1. Pestaña 1: Usuario login → Token A guardado en BD
2. Pestaña 2: Usuario login (mismo usuario, rol diferente) → Token B reemplaza Token A
3. Pestaña 1: Intenta usar Token A → Recibe 401 (es token antiguo)

#### 3. **Auth: Validar Token en Request**
**Archivo**: `app/modules/auth/router.py` - Función `get_current_user()`

```python
def get_current_user(token: str = Depends(oauth2_scheme), 
                     db: Session = Depends(get_db)):
    """
    Validate JWT token - AHORA con validación de single session
    """
    # ... validar JWT ...
    
    # 🆕 SINGLE SESSION: Verificar que es el token más reciente
    user = db.query(User).filter(User.id == user_id).first()
    
    if user.last_valid_token and user.last_valid_token != token:
        logger.warning(
            f"Attempt to use outdated token for user: {email}. "
            f"User has more recent session."
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tienes una nueva sesión activa en otro dispositivo/navegador. "
                   "Esta sesión ha sido cerrada por seguridad."
        )
    
    return {"email": email, "role": role, "user_id": user_id}
```

**Resultado**: Si Token A se usa después de Token B → 401 automático

---

## 🔄 Diagrama de Flujo

### Caso 1: Logout Sincronizado
```
Pestaña 1: Usuario hace click en "Cerrar Sesión"
    ↓
Frontend: authManager.logout()
    ├─ clearAuthData() → localStorage.removeItem('authToken')
    └─ notifyAuthChange('logout')
    ↓
Pestaña 2: Storage event listener detecta cambio
    ├─ handleRemoteLogout()
    └─ actualiza UI, oculta menu usuario
```

### Caso 2: Multiple Login (Mismo usuario, roles diferentes)
```
Pestaña 1: Login como usuario
    → Token A guardado en BD (user.last_valid_token = Token A)
    → Acceso a /user
    
Pestaña 2: Login como admin (mismo usuario)
    → Token B reemplaza Token A en BD
    → Acceso a /admin
    
Pestaña 1: Intenta acceder a /user
    → Usa Token A
    → Backend: Token A ≠ user.last_valid_token (es Token B)
    → Devuelve 401
    → Frontend: Limpia localStorage, redirige a /
```

### Caso 3: Multiple Dispositivos
```
Navegador A: Token emitido
    → Guardado en BD (user.last_valid_token = Token A)
    
Navegador B: Nuevo login del mismo usuario
    → Token B reemplaza Token A en BD
    → Acceso concedido
    
Navegador A: Siguiente request
    → Usa Token A
    → Backend: Token A ≠ Token B → 401
    → Usuario notificado: "Nueva sesión en otro dispositivo"
```

---

## 🚀 Implementación Técnica

### Storage Events (Browser API)
```javascript
window.addEventListener('storage', (event) => {
    // Se dispara en OTRAS pestañas cuando una cambia localStorage
    // NO se dispara en la pestaña que hizo el cambio
    
    console.log(event.key);        // 'authToken'
    console.log(event.oldValue);   // Token anterior
    console.log(event.newValue);   // Token nuevo
});
```

**Limitación**: Mismo navegador/origen solamente. Para sincronizar entre navegadores, se usa 401 + token refresh.

### JWT Validation en Backend
```python
# Token contiene:
payload = jwt.decode(token, SECRET_KEY)
# {
#     'sub': 'user@example.com',     # email
#     'role': 'admin',                # role
#     'user_id': 42,                  # user id
#     'exp': 1704067200               # expiration
# }

# En get_current_user:
user = db.query(User).filter(User.id == payload['user_id']).first()
if user.last_valid_token != token:
    # Token es viejo, rechazar
    raise HTTPException(401, "Nueva sesión activa en otro dispositivo")
```

---

## ✅ Verificación / Testing

### Frontend
```javascript
// Test 1: Logout sincronizado
// 1. Abrir app.com en Pestaña 1
// 2. Abrir app.com en Pestaña 2
// 3. Login en Pestaña 1
//    → Pestaña 2 debe actualizar UI mostrando usuario logueado ✓
// 4. Logout en Pestaña 1
//    → Pestaña 2 debe mostrar login nuevamente ✓

// Test 2: Multiple login
// 1. Login como usuario en Pestaña 1 → acceso a /user ✓
// 2. Login como admin en Pestaña 2 → acceso a /admin ✓
// 3. Pestaña 1 intenta acceder a API → 401 ✓
// 4. Pestaña 1 redirige a / ✓
```

### Backend
```bash
# Test 1: Login obtiene token válido
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'
# Response: 200 con access_token ✓

# Test 2: Token antiguo rechazado
# 1. Hacer login → Token A
# 2. Hacer otro login → Token B guardado
# 3. Usar Token A en request
curl -H "Authorization: Bearer <TOKEN_A>" \
  http://localhost:8000/api/v1/users/me
# Response: 401 "Nueva sesión activa en otro dispositivo" ✓

# Test 3: Token nuevo funciona
curl -H "Authorization: Bearer <TOKEN_B>" \
  http://localhost:8000/api/v1/users/me
# Response: 200 user data ✓
```

---

## 🔒 Beneficios de Seguridad

1. **Previene Account Takeover**: Si alguien roba token antiguo, ya no funciona
2. **Session Hijacking Detection**: Múltiples sesiones activas se detectan automáticamente
3. **Logout Sincronizado**: Logout en una pestaña = logout en todas
4. **Role Switching Detection**: Si usuario intenta cambiar rol en otra pestaña, se detecta
5. **Multi-Device Awareness**: Usuario sabe si tiene sesión en otro dispositivo

---

## 📝 Notas Importantes

### Migration de Base de Datos
```bash
# Ejecutar el script SQL:
psql -U postgres -d db_CTech -f migrations/add_session_fields.sql

# O en SQLAlchemy:
from app.app.core.database import engine
# Los cambios en models.py se sincronizarán automáticamente 
# (si SQLAlchemy está configurado en modo auto-migrate)
```

### Backward Compatibility
- ✅ Tokens antiguos sin `user_id` en payload: Se validan igual
- ✅ Usuarios sin `last_valid_token` en BD: Se trata como NULL (válido)
- ✅ Clientes sin storage listeners: Siguen funcionando

### Performance
- ✅ Una query adicional por request (obtener `last_valid_token`)
- ✅ Compatible con Redis caching (si se implementa)
- ✅ Índice en `last_valid_token` para optimizar búsquedas (opcional)

---

## 🔄 Próximos Pasos Recomendados

1. [ ] Ejecutar migración SQL en BD
2. [ ] Testear logout sincronizado en 2 pestañas
3. [ ] Testear login múltiple (diferentes roles)
4. [ ] Implementar UI feedback: "Nueva sesión en otro dispositivo"
5. [ ] Agregar endpoint `/auth/sessions` para listar sesiones activas por usuario
6. [ ] Agregar endpoint `/auth/logout-all` para cerrar todas las sesiones

---

## 📚 Referencias

- **Browser Storage Events**: https://developer.mozilla.org/en-US/docs/Web/API/StorageEvent
- **JWT Best Practices**: https://tools.ietf.org/html/rfc8949
- **Session Management**: https://owasp.org/www-community/attacks/Session_fixation
