# CTech Backend — Requerimientos Técnicos

> Especificación técnica del backend de la plataforma CTech.
> Proyecto SENA — Ficha 2995403

---

## 1. Entorno de Ejecución

| Requerimiento | Detalle |
|---|---|
| **Lenguaje** | Python 3.11 o superior |
| **Sistema operativo** | Windows 10/11, Linux (Ubuntu 20.04+), macOS |
| **Gestor de entorno** | `venv` (entorno virtual Python) |
| **Servidor de aplicación** | Uvicorn (ASGI, modo `--reload` para desarrollo) |

---

## 2. Dependencias del Proyecto

Archivo: `requirements.txt`

| Paquete | Versión mínima | Función |
|---|---|---|
| `fastapi` | última estable | Framework web API REST |
| `uvicorn` | última estable | Servidor ASGI para FastAPI |
| `sqlalchemy` | última estable | ORM para modelado y consulta de BD |
| `psycopg2-binary` | última estable | Driver PostgreSQL para SQLAlchemy |
| `python-jose[cryptography]` | última estable | Generación y validación de JWT (HS256) |
| `passlib[bcrypt]` | última estable | Hashing seguro de contraseñas con bcrypt |
| `pydantic-settings` | v2+ | Gestión de configuración desde `.env` |
| `python-dotenv` | última estable | Carga de variables de entorno |
| `email-validator` | última estable | Validación de formato de emails con Pydantic |

### Instalación

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux / macOS
pip install -r requirements.txt
```

---

## 3. Base de Datos

| Requerimiento | Detalle |
|---|---|
| **Motor** | PostgreSQL 15 o superior |
| **Driver** | psycopg2-binary (incluido en requirements.txt) |
| **Conexión** | Configurada vía variables de entorno en `.env` |
| **ORM** | SQLAlchemy con declarative Base |
| **Creación de tablas** | Automática al iniciar el servidor (`Base.metadata.create_all`) |
| **Seed de datos** | Automático al iniciar el servidor (`init_db.seed_data`) |

### Cadena de conexión
```
postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}
```

### Variables de entorno requeridas (`.env`)

```env
DB_USER=postgres
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ctech_db

JWT_SECRET_KEY=clave_secreta_larga_y_segura
ACCESS_TOKEN_EXPIRE_MINUTES=1440

ADMIN_EMAIL=admin@ctech.com
ADMIN_PASSWORD=password_del_admin

CLOUDINARY_CLOUD_NAME=tu_cloud_name
CLOUDINARY_API_KEY=tu_api_key
CLOUDINARY_API_SECRET=tu_api_secret
```

---

## 4. Seguridad

### Autenticación
- **Protocolo:** JWT (JSON Web Token)
- **Algoritmo de firma:** HS256
- **Tiempo de expiración:** 1440 minutos (24 horas, configurable en `.env`)
- **Formato del header:** `Authorization: Bearer <token>`
- **Tokenización:** `python-jose[cryptography]`

### Contraseñas
- **Algoritmo:** bcrypt
- **Librería:** `passlib`
- **Proceso:**
  - Al registrar: `pwd_context.hash(password)` → almacenado en `password_hash`
  - Al login: `pwd_context.verify(plain, hashed)` → comparación segura

### Logout / Invalidación de Tokens
- Los tokens invalidados se almacenan en la tabla `token_blocklist`.
- Cada solicitud protegida verifica que el token no esté en dicha lista.

### CORS
- Configurado con `allow_origin_regex="https?://.*"` para desarrollo.
- En producción: restringir a los dominios autorizados del frontend.

---

## 5. Almacenamiento de Imágenes

| Requerimiento | Detalle |
|---|---|
| **Servicio** | Cloudinary |
| **Uso** | Imágenes de eventos y logos de comunidades |
| **Integración** | `core/cloudinary_service.py` centraliza la conexión |
| **Configuración** | Variables `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET` en `.env` |
| **Retorno** | URL pública de la imagen almacenada en Cloudinary |

---

## 6. API REST

| Requerimiento | Detalle |
|---|---|
| **Framework** | FastAPI |
| **Prefijo global** | `/api/v1` |
| **Formato de datos** | JSON |
| **Validación de entrada** | Pydantic v2 (schemas) |
| **Documentación automática** | Swagger UI en `/docs`, ReDoc en `/redoc` |
| **Módulos registrados** | 7 módulos (auth, users, communities, events, metrics, notifications, admin) |

---

## 7. Roles y Control de Acceso (RBAC)

| ID | Nombre | Permisos |
|---|---|---|
| 1 | `admin` | Acceso total al sistema, panel administrativo |
| 3 | `leader` | Gestión de su comunidad y creación de eventos |
| 4 | `user` | Acceso a eventos de su comunidad |

- Los roles se crean automáticamente en el seed al iniciar el servidor.
- El rol se incluye en el payload del JWT como `"role": "admin"|"leader"|"user"`.
- FastAPI verifica el rol mediante el `Depends(get_current_user)` en cada endpoint protegido.

---

## 8. Inicialización del Servidor

```bash
# Desde el directorio /backend con el .venv activado:
uvicorn app.main:app --reload --port 8000

# O usando el script de Windows:
run_backend.bat
```

Al iniciar, el servidor:
1. Conecta a PostgreSQL usando las variables del `.env`.
2. Crea automáticamente todas las tablas si no existen.
3. Ejecuta el seed (`init_db.py`) para garantizar roles y admin.
4. Registra los 7 módulos bajo `/api/v1`.
5. Expone la API en `http://localhost:8000`.

---

## 9. Pruebas

| Tipo | Ubicación | Herramientas |
|---|---|---|
| Pruebas unitarias | `app/tests/` | pytest |
| Pruebas de integración | `app/tests/` | pytest + httpx (TestClient de FastAPI) |
| Pruebas manuales | `http://localhost:8000/docs` | Swagger UI |

```bash
# Ejecutar pruebas
pytest app/tests/ -v
```

---

## 10. Consideraciones para Producción

- [ ] Cambiar `JWT_SECRET_KEY` por una clave larga y aleatoria (mínimo 32 caracteres).
- [ ] Restringir CORS a los dominios del frontend en producción.
- [ ] Usar variables de entorno del servidor (no archivo `.env` en producción).
- [ ] Configurar HTTPS en el servidor (certificado SSL).
- [ ] Considerar migraciones con **Alembic** en lugar de `create_all` al cambiar modelos.
- [ ] Habilitar rate limiting para endpoints de autenticación.
- [ ] Revisar y activar los guards de autenticación en módulos donde están comentados (communities, etc.).
