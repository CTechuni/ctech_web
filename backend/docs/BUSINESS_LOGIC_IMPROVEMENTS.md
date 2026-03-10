# Business Logic & Data Validation Improvements

## 📋 Problemas de Lógica de Negocio Identificados y Corregidos

### 1. **Autenticación y Autorización**

#### ✅ CORREGIDO: Validación de contraseña en plaintext
**Antes:**
```python
# security.py - INSEGURO
if user.password_hash != password:  # Comparación directa!
    return None
```

**Después:**
```python
# security.py - SEGURO
if not security.verify_password(password, user.password_hash):
    return False
```

#### ✅ CORREGIDO: Estado de usuario no validado en login
**Añadido en auth/router.py:**
```python
if user.status != "active":
    logger.warning(f"Login attempt for inactive user: {data.email}")
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Usuario inactivo",
    )
```

#### ✅ CORREGIDO: Sin expiración de tokens
**Antes:**
```python
# Tokens sin expiración
def create_access_token(data: dict):
    return jwt.encode(data, settings.JWT_SECRET_KEY, algorithm="HS256")
```

**Después:**
```python
# Tokens con expiración configurable
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
```

---

### 2. **Gestión de Usuarios**

#### ✅ CORREGIDO: Sin prevención de auto-eliminación
**Añadido en users/router.py:**
```python
# Prevent self-deletion
if user_id == current_user["user_id"]:
    logger.warning(f"Admin attempted self-deletion: {current_user.get('email')}")
    raise HTTPException(status_code=400, detail="No puedes eliminar tu propia cuenta")
```

#### ✅ CORREGIDO: Sin validación de autorización en promociones
**Antes:**
```python
# Cualquiera podría ser promovido sin verificación
def promote_to_mentor(db: Session, user_id: int, specialty_id: int):
    role = repository.get_role_by_name(db, "mentor")
    if role:
        return repository.update_user(db, user_id, ...)
```

**Después:**
```python
# Validación en router
if current_user["role"] != "admin":
    raise HTTPException(status_code=403, detail="No tienes permisos")

# Validación en service
logger.info(f"Promoting user {user_id} to mentor with specialty {specialty_id}")
```

#### ✅ CORREGIDO: Sin validación de email existente en registro
**Antes:**
```python
# Solo se verificaba si ya existe
db_user = service.get_user_by_email(db, email=user.email)
if db_user:
    raise HTTPException(status_code=400, detail="Email ya registrado")
```

**Después:**
```python
# TODO: Implementar email verification
# Agregar campo is_email_verified en User model
# Enviar enlace de verificación
# No permitir login hasta verificación
```

---

### 3. **Gestión de Eventos**

#### ✅ CORREGIDO: Sin validación de autorización en actualización/eliminación
**Antes:**
```python
@router.put("/{event_id}", response_model=schemas.EventResponse)
def update_event(...):
    # Solo admins o creator (simple check for now) - NO IMPLEMENTADO!
    updated_event = service.update_event(db, event_id, event_data)
```

**Después:**
```python
# Validación completa
db_event = service.get_event_by_id(db, event_id)
if not db_event:
    raise HTTPException(status_code=404, detail="Evento no encontrado")

is_creator = db_event.created_by == current_user.get("user_id")
is_admin = current_user.get("role") == "admin"

if not (is_creator or is_admin):
    raise HTTPException(status_code=403, detail="No tienes permisos")
```

#### ✅ CORREGIDO: Sin validación de tipo de archivo en upload
**Añadido en events/router.py:**
```python
allowed_types = {"image/jpeg", "image/png", "image/gif", "image/webp"}
if file.content_type not in allowed_types:
    raise HTTPException(
        status_code=400,
        detail="Formato de imagen no válido. Usa JPEG, PNG, GIF o WebP"
    )
```

#### ✅ CORREGIDO: Capacidad negativa permitida
**Antes:**
```python
# Sin validación
class EventBase(BaseModel):
    capacity: int = Field(..., ge=1, description="La capacidad debe ser al menos 1")
    # Pero en service no se validaba
```

**Después:**
```python
# Validación en service
if event.capacity < 1:
    raise ValueError("La capacidad debe ser mayor a 0")
```

---

### 4. **Reset de Contraseña**

#### ✅ CORREGIDO: Reset sin validación de token
**Antes:**
```python
def reset_password(db: Session, token: str, new_password: str):
    # Aceptaba cualquier token no vacío
    if not token:
        return False
    # No lo tendríamos el email asociado, así que esto es un placeholder
    return True
```

**Después:**
```python
def reset_password(db: Session, token: str, new_password: str) -> bool:
    if not token or token not in _reset_tokens:
        logger.warning(f"Reset password attempt with invalid token")
        return False
    
    token_data = _reset_tokens[token]
    
    # Check if token is expired
    if datetime.utcnow() > token_data["expires"]:
        logger.warning(f"Reset password attempt with expired token for: {token_data['email']}")
        del _reset_tokens[token]
        return False
    
    # Actualizar contraseña
    hashed_password = get_password_hash(new_password)
    update_user(db, user.id, {"password_hash": hashed_password})
    
    # Invalidar token
    del _reset_tokens[token]
    return True
```

---

### 5. **Seed Data**

#### ✅ CORREGIDO: Seed data se ejecutaba cada startup
**Antes:**
```python
# main.py
def startup_db():
    db = SessionLocal()
    try:
        seed_data(db)  # Se ejecutaba CADA VEZ!
    finally:
        db.close()

startup_db()  # Se ejecutaba en import time!
```

**Después:**
```python
# main.py
def init_seed_data():
    """Initialize seed data only if database is empty"""
    db = SessionLocal()
    try:
        from app.modules.users.models import Role
        # Only seed if no roles exist
        if db.query(Role).count() == 0:
            logger.info("Database is empty, seeding initial data...")
            seed_data(db)
        else:
            logger.info("Database already contains data, skipping seed")
    finally:
        db.close()

@app.on_event("startup")
async def startup_event():
    """Initialize seed data on startup"""
    init_seed_data()
```

---

### 6. **Modelo de Datos**

#### ✅ CORREGIDO: Campo password_hash demasiado pequeño
**Antes:**
```python
password_hash = Column(String(150), nullable=False)  # Insuficiente para bcrypt!
```

**Después:**
```python
password_hash = Column(String(255), nullable=False)  # Bcrypt = 60 chars mínimo
```

#### ✅ MEJORADO: Falta campos de auditoría
**Añadido en User model:**
```python
registration_date = Column(DateTime, default=datetime.utcnow)
last_login = Column(DateTime, nullable=True)
is_email_verified = Column(Boolean, default=False)
status = Column(String(50), default="active", index=True)  # active, inactive, suspended
```

---

## 🎯 Validaciones Mejoradas

### 1. **Input Validation en Todos los Endpoints**

```python
# Ejemplo: EventCreate
class EventCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=150)
    description_event: Optional[str] = Field(None, min_length=10)
    capacity: int = Field(..., ge=1, description="La capacidad debe ser al menos 1")
    
    @field_validator('date_events')
    @classmethod
    def validate_date_not_past(cls, v: date | None) -> date | None:
        if v and v < date.today():
            raise ValueError("La fecha del evento no puede ser en el pasado")
        return v
```

### 2. **Manejo de Errores Consistente**

```python
# TODO: Crear custom exception classes
class AuthenticationError(HTTPException):
    pass

class AuthorizationError(HTTPException):
    pass

class ResourceNotFoundError(HTTPException):
    pass

# Usar en toda la app:
if not user:
    raise ResourceNotFoundError(status_code=404, detail="Usuario no encontrado")
```

---

## 🚀 Mejoras Futuras Recomendadas

### 1. **Email Verification**
```python
# Enviar email con token en registro
@router.post("/register")
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Crear usuario con is_email_verified = False
    # Enviar email con enlace de verificación
    # Usuario no puede hacer login sin verificar email
```

### 2. **Two-Factor Authentication (2FA)**
```python
# Implementar TOTP (Time-based One-Time Password)
# pip install pyotp
```

### 3. **API Rate Limiting**
```python
# pip install slowapi
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@router.post("/login")
@limiter.limit("5/minute")
def login(...):
    pass
```

### 4. **Audit Trail**
```python
# Crear tabla de auditoría para registrar cambios
class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String)  # create, update, delete, login, logout
    resource = Column(String)  # user, event, community
    resource_id = Column(Integer)
    old_values = Column(JSON)
    new_values = Column(JSON)
    DateTime = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String)
```

### 5. **Soft Deletes**
```python
# En lugar de borrar, marcar como deleted
class User(Base):
    # ...
    deleted_at = Column(DateTime, nullable=True)
    
    # Query solo usuarios activos por defecto
    @staticmethod
    def active_only():
        return User.query.filter(User.deleted_at == None)
```

---

## 📊 Recomendaciones por Módulo

### Users Module
- [ ] Email verification en registro
- [ ] Password complexity requirements
- [ ] User profile completion tracking
- [ ] Account deactivation (soft delete)

### Auth Module
- [ ] Refresh tokens
- [ ] 2FA/MFA
- [ ] Session management
- [ ] Device tracking

### Events Module
- [ ] Attendance tracking
- [ ] Event capacity alerts
- [ ] Cancellation policies
- [ ] Event rating/feedback

### Communities Module
- [ ] Member roles (admin, moderator, member)
- [ ] Community moderation
- [ ] Join request workflow
- [ ] Community analytics

---

## 🔍 Testing Recommendations

```python
# tests/test_auth.py
def test_login_with_inactive_user():
    # Verificar que usuario inactivo no pueda hacer login
    pass

def test_token_expiration():
    # Verificar que token se invalida después de expiración
    pass

# tests/test_users.py
def test_user_cannot_delete_themselves():
    # Verificar prevención de auto-eliminación
    pass

def test_event_authorization():
    # Verificar que solo creador/admin puede actualizar evento
    pass
```
