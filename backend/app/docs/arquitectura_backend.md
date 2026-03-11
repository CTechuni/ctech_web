# CTech Backend — Arquitectura

## Descripción General

El backend de CTech es una **API REST** construida con **FastAPI** y **SQLAlchemy**. Sigue una arquitectura **modular por dominio**, donde cada entidad de negocio tiene su propio módulo con responsabilidades separadas.

**Servidor:** Uvicorn (ASGI)
**ORM:** SQLAlchemy (declarative base)
**Base de datos:** PostgreSQL (psycopg2-binary)

---

## Estructura de Directorios

```
backend/
├── app/
│   ├── main.py                  ← Entry point: registra routers, crea tablas, ejecuta seed
│   ├── core/
│   │   ├── config.py            ← Settings con pydantic_settings (lee .env)
│   │   ├── database.py          ← Engine, SessionLocal y get_db dependency
│   │   ├── security.py          ← bcrypt (hash/verify) + JWT (crear token)
│   │   ├── cloudinary_service.py← Integración con Cloudinary para imágenes
│   │   └── logger.py            ← Logger centralizado
│   ├── db/
│   │   ├── base_api.py          ← Importa todos los modelos → Base.metadata.create_all
│   │   └── init_db.py           ← Seed: crea roles y admin por defecto al iniciar
│   ├── modules/
│   │   ├── auth/                ← Autenticación y sesiones
│   │   ├── users/               ← Usuarios y perfiles
│   │   ├── communities/         ← Comunidades tecnológicas
│   │   ├── events/              ← Eventos (públicos/privados)
│   │   ├── metrics/             ← Métricas del dashboard admin
│   │   ├── notifications/       ← Notificaciones globales/admin
│   │   └── admin/               ← Panel de administración (puntos de entrada admin)
│   ├── docs/                    ← Esta documentación
│   └── tests/                   ← Pruebas unitarias e integración
├── migrations/                  ← Scripts de migración SQL
├── requirements.txt
├── .env                         ← Variables de entorno (no versionar)
└── run_backend.bat              ← Script de inicio rápido (Windows)
```

---

## Estructura Interna de cada Módulo

Cada módulo sigue el mismo patrón de capas:

```
módulo/
├── __init__.py
├── models.py      ← Modelos SQLAlchemy (tablas en PostgreSQL)
├── schemas.py     ← Schemas Pydantic (validación I/O de la API)
├── router.py      ← Rutas FastAPI (endpoints HTTP)
└── service.py     ← Lógica de negocio (operaciones CRUD y reglas)
```

---

## Capa Core

### `core/config.py` — Settings
Usa `pydantic_settings.BaseSettings` para leer variables del `.env`:

| Variable | Descripción |
|---|---|
| `DB_USER / DB_PASSWORD / DB_HOST / DB_PORT / DB_NAME` | Conexión PostgreSQL |
| `JWT_SECRET_KEY` | Clave para firmar tokens JWT |
| `ALGORITHM` | Algoritmo JWT (HS256) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Expiración del token (default: 1440 min = 24 h) |
| `ADMIN_EMAIL / ADMIN_PASSWORD` | Credenciales del admin creado en el seed |
| `CLOUDINARY_CLOUD_NAME / API_KEY / API_SECRET` | Integración Cloudinary |

### `core/database.py` — Conexión
- Crea el `engine` SQLAlchemy con la `DATABASE_URL` construida desde Settings.
- Expone `SessionLocal` (fábrica de sesiones) y `get_db` (dependency de FastAPI).

### `core/security.py` — Seguridad
- **`get_password_hash(password)`** — Hashea con bcrypt.
- **`verify_password(plain, hashed)`** — Verifica contraseña contra hash bcrypt.
- **`create_access_token(data, expires_delta)`** — Genera JWT firmado con HS256.

---

## Flujo de Arranque (`main.py`)

```
1. Base.metadata.create_all(engine)  → Crea todas las tablas si no existen
2. seed_data(db)                     → Inserta roles y admin por defecto
3. app = FastAPI(...)                → Instancia la aplicación
4. app.add_middleware(CORS)          → Habilita CORS para cualquier origen
<!-- 5. app.include_router(...)           → Registra los módulos en /api/v1 -->
```

---

## Seguridad y Autenticación

### Flujo de Login
```
Cliente → POST /api/v1/auth/login
        → Busca usuario por email en BD
        → Verifica password con bcrypt
        → Genera JWT con {sub: email, role: nombre_rol, id: user_id}
        → Retorna access_token + datos del usuario
```

### Flujo de Solicitud Protegida
```
Cliente → Header: Authorization: Bearer <token>
        → FastAPI extrae token con OAuth2PasswordBearer
        → service.get_current_user() decodifica JWT con python-jose
        → Si token en token_blocklist → 401 Unauthorized
        → Si expirado o firma inválida → 401 Unauthorized
        → Si válido → inyecta {user_id, email, role} al endpoint
```

### Logout (Token Blocklist)
Al hacer logout, el token se añade a la tabla `token_blocklist`. Cada solicitud verifica que el token no esté en esa tabla antes de procesarla.

---

## Middleware CORS

Configurado para aceptar cualquier origen (`allow_origin_regex="https?://.*"`), métodos y headers. En producción se debe restringir a los dominios autorizados.

---

## Seed de Datos (`db/init_db.py`)

Al iniciar el servidor, se ejecuta automáticamente un seed que garantiza:

1. **Roles creados:**
   - `id=1` → `admin`
   - `id=3` → `leader`
   - `id=4` → `user`

2. **Usuario administrador creado** con las credenciales definidas en `.env` (`ADMIN_EMAIL`, `ADMIN_PASSWORD`).

> Si los datos ya existen, el seed no los duplica.

---

## Integración con Cloudinary

Las imágenes de eventos se almacenan en **Cloudinary**. El módulo `core/cloudinary_service.py` centraliza la conexión. Los endpoints de subida de imágenes (`POST /events/upload`) reciben un `UploadFile` y retornan la URL pública de Cloudinary.

---

## Convenciones del Código

| Aspecto | Convención |
|---|---|
| Nombres de tablas | `snake_case` en plural (`users`, `communities`) |
| Primary keys | `id` o `id_{entidad}` (ej: `id_community`, `id_rol`) |
| Foreign keys | `{entidad}_id` (ej:`community_id`) |
| Schemas de entrada | `{Entidad}Create` / `{Entidad}Update` |
| Schemas de salida | `{Entidad}Response` |
| Prefijo de rutas | `/api/v1/{módulo}` |
