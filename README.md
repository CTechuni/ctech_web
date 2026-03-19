# CTech Platform

> **Plataforma de comunidades tecnológicas en Colombia**
> Proyecto SENA — Ficha 2995403

---

## Descripción del Proyecto

CTech es una plataforma **gratuita** dirigida a **comunidades tecnológicas en Colombia**. Su propósito es conectar a personas interesadas en tecnología con comunidades organizadas, proporcionándoles acceso a **eventos** de forma centralizada.

La plataforma no requiere pago alguno. El crecimiento de la comunidad se logra a través de **eventos públicos** y el **intercambio presencial del código de comunidad** por parte del líder.

---

## Modelo de Funcionamiento

### Acceso Gratuito
La plataforma es **100% gratuita**. No hay costo de inscripción, membresía ni acceso a contenido.

### Comunidades Tecnológicas
CTech está dirigida a **comunidades de tecnología en Colombia**: grupos organizados por temática (desarrollo web, mobile, datos, ciberseguridad, etc.).

Cada comunidad tiene:
- Un **Líder** responsable de gestionar la comunidad.
- Su propio catálogo de **eventos** (públicos y privados).
- Un **código de comunidad** único que funciona como llave de acceso.

### Ingreso por Código
El **Líder** comparte de forma **presencial** el código único de su comunidad. Con ese código el usuario puede:
- Registrarse y unirse a la comunidad.
- Acceder a todos sus **eventos internos**.

> El código NO se publica en la plataforma — se entrega en persona, asegurando que solo personas realmente interesadas accedan al contenido privado.

### Eventos: Público vs Privado

| Visibilidad | Acceso |
|---|---|
| **Público** | Visible para cualquier visitante sin registro. Sirve como vitrina de atracción. |
| **Privado** | Solo visible para miembros registrados de la comunidad. |

**Flujo de aprobación de eventos:** `draft → pending → approved | rejected`

- Líder y admin crean eventos que se aprueban automáticamente.
- El sistema notifica a los usuarios al publicarse un evento.
- Al inscribirse, el usuario recibe notificación in-app y correo de confirmación.

---

## Objetivo General

Desarrollar una plataforma web que centralice la gestión de **comunidades tecnológicas** y sus **eventos** en Colombia, facilitando el acceso, la inscripción y la comunicación entre miembros bajo un sistema organizado por roles.

---

## Objetivos Específicos

1. **Gestionar comunidades tecnológicas** — Crear, organizar y administrar comunidades temáticas.
2. **Administrar eventos** — Registrar, publicar y gestionar eventos (presenciales y virtuales) con flujo de aprobación.
3. **Implementar RBAC** — Garantizar que cada rol (Admin, Líder, Usuario) acceda solo a sus funciones.
4. **Proveer métricas** — Estadísticas de uso para administradores y líderes.
5. **Asegurar seguridad** — Autenticación JWT, hashing bcrypt, validación Pydantic.

---

## Público Objetivo

| Perfil | Descripción |
|---|---|
| **Desarrolladores / Programadores** | Personas que buscan conectar con comunidades tecnológicas |
| **Estudiantes de tecnología** | Estudiantes de carreras técnicas y tecnológicas |
| **Líderes de comunidad tech** | Personas que organizan comunidades tecnológicas locales |
| **Administrativos SENA / Instituciones** | Gestores que supervisan comunidades |

> **País de aplicación: Colombia únicamente.**

---

## Arquitectura General

```
CTech/
├── backend/       → API REST (FastAPI + PostgreSQL)
└── frontend/      → Interfaz web (Astro + Bootstrap 5)
```

- El **backend** expone una API REST en `/api/v1/`.
- El **frontend** consume la API con `fetch` nativo desde el cliente.
- La autenticación es **stateless via JWT**, almacenado en `localStorage`.

---

## Stack Tecnológico

### Backend

| Tecnología | Rol |
|---|---|
| **Python 3.11+** | Lenguaje principal |
| **FastAPI** | Framework web / API REST |
| **SQLAlchemy 2.0** | ORM |
| **PostgreSQL 15+** | Base de datos relacional |
| **python-jose** | JWT |
| **passlib (bcrypt)** | Hashing de contraseñas |
| **Pydantic v2** | Validación de datos |
| **Cloudinary** | Almacenamiento de imágenes |

### Frontend

| Tecnología | Rol |
|---|---|
| **Astro 5.x** | Framework SSG/SSR híbrido |
| **TypeScript 5.x** | Tipado estático |
| **Bootstrap 5.3** | Framework CSS |
| **JavaScript ESM** | Lógica de cliente (fetch, auth) |

---

## Sistema de Autenticación y RBAC

- **JWT** con HS256. Token con expiración configurable (por defecto 24 h).
- **bcrypt** para hashing de contraseñas.
- **Token blocklist** para invalidar tokens en logout.
- **RBAC — 3 roles:**
  - `admin` (rol_id 1) — acceso total al sistema
  - `leader` (rol_id 3) — gestión de su comunidad y eventos
  - `user` (rol_id 4) — acceso a eventos e inscripciones
- **Seed automático**: `init_db.py` crea roles y usuario admin al iniciar si no existen.

---

## Base de Datos

- **Motor**: PostgreSQL
- **ORM**: SQLAlchemy con declarative base
- **Tablas activas:**
  - `users`, `roles`, `profiles`
  - `communities`
  - `events`, `event_registrations`
  - `notifications`
  - `token_blocklist`

---

## Módulos del Backend (`/api/v1/`)

| Módulo | Prefijo | Descripción |
|---|---|---|
| **auth** | `/api/v1/auth` | Login, registro, logout, reset de contraseña |
| **users** | `/api/v1/users` | CRUD usuarios, cambio de rol, perfil |
| **communities** | `/api/v1/communities` | Gestión de comunidades, logo |
| **events** | `/api/v1/events` | CRUD eventos, flujo aprobación, inscripciones |
| **metrics** | `/api/v1/metrics` | Dashboard admin y líder |
| **notifications** | `/api/v1/notifications` | Notificaciones in-app |
| **admin** | `/api/v1/admin` | Operaciones exclusivas del administrador |

### Endpoints de Eventos destacados

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/events/` | Listado con filtros (skip, limit, upcoming_only, community_id, event_type) |
| `GET` | `/events/pending` | Eventos pendientes de aprobación |
| `GET` | `/events/upcoming` | Próximos 5 eventos aprobados |
| `GET` | `/events/my` | Eventos creados por el usuario actual |
| `GET` | `/events/{id}` | Detalle de un evento |
| `GET` | `/events/{id}/registration` | Verifica si el usuario está inscrito |
| `GET` | `/events/{id}/attendees` | Lista de asistentes (líder/admin) |
| `POST` | `/events/` | Crear evento |
| `POST` | `/events/upload-image` | Subir imagen (JPG/PNG/WEBP/GIF, máx 5MB) |
| `PATCH` | `/events/{id}/approve` | Aprobar evento |
| `PATCH` | `/events/{id}/reject` | Rechazar evento |
| `POST` | `/events/{id}/register` | Inscribirse a un evento |
| `DELETE` | `/events/{id}/register` | Cancelar inscripción |

Cada módulo sigue la estructura de 4 capas:
```
módulo/
├── models.py    → Modelos SQLAlchemy
├── schemas.py   → Schemas Pydantic
├── repository.py → Queries a la DB
├── service.py   → Lógica de negocio
└── router.py    → Rutas FastAPI
```

---

## Estructura del Frontend

### Layouts por Rol

| Layout | Uso |
|---|---|
| **AdminLayout** | Panel de administración |
| **LeaderLayout** | Panel de líderes |
| **UserLayout** | Panel de usuarios |
| **MainLayout** | Páginas públicas |

### Páginas Implementadas

**Admin (`/admin`)**
- Dashboard con KPIs y gráficas
- Gestión de usuarios, comunidades, líderes
- Gestión de eventos + calendario
- Perfil y configuración

**Leader (`/leader`)**
- Dashboard con estadísticas de comunidad
- Gestión de eventos + calendario
- Gestión de miembros

**User (`/user`)**
- Dashboard, perfil, configuración
- Eventos y calendario

**Públicas**
- Landing page
- Reset de contraseña

### Utilidades del Cliente

| Archivo | Descripción |
|---|---|
| `utils/auth.js` | Gestión JWT, validación de roles, redirección automática |
| `utils/communities-logic.js` | Lógica CRUD comunidades |
| `utils/escape.js` | Sanitización de HTML |

---

## Estructura del Repositorio

```
CTech/
├── backend/
│   ├── app/
│   │   ├── core/          → config, database, security, logger, cloudinary, email
│   │   ├── db/            → base_api.py, init_db.py (seed)
│   │   ├── modules/       → auth, users, communities, events, metrics, notifications, admin
│   │   └── main.py        → entry point FastAPI
│   ├── migrations/        → scripts SQL
│   ├── rements.txt
│   ├── .env               → variables de entorno (no commitear)
│   └── run_backend.bat    → inicio rápido (Windows)
│
├── frontend/
│   ├── src/
│   │   ├── components/    → componentes por rol (admin/, leader/, user/, shared/)
│   │   ├── layouts/       → layouts por rol
│   │   ├── pages/         → páginas por rol
│   │   ├── styles/        → estilos globales
│   │   ├── utils/         → auth.js, lógica cliente
│   │   └── config/        → constantes (API URL)
│   ├── public/            → assets estáticos
│   ├── astro.config.mjs
│   └── package.json
│
├── reset_admin.py         → script para recuperar acceso al admin
└── README.md
```

---

## Cómo Levantar el Proyecto

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con credenciales de PostgreSQL, JWT secret, Cloudinary y Gmail

uvicorn app.main:app --reload --port 8000
# O usar: run_backend.bat
```

API disponible en: `http://localhost:8000`
Documentación: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Aplicación disponible en: `http://localhost:4321`

---

## Variables de Entorno

### Backend (`.env`)

```env
DB_USER=postgres
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ctech_db

JWT_SECRET_KEY=clave_super_secreta
ACCESS_TOKEN_EXPIRE_MINUTES=1440

ADMIN_EMAIL=admin@ctech.com
ADMIN_PASSWORD=password_segura

CLOUDINARY_CLOUD_NAME=tu_cloud_name
CLOUDINARY_API_KEY=tu_api_key
CLOUDINARY_API_SECRET=tu_api_secret

GMAIL_USER=tu_correo@gmail.com
GMAIL_APP_PASSWORD=tu_app_password
```

### Frontend (`.env`)

```env
PUBLIC_API_URL=http://localhost:8000
```

---

## Estado del Proyecto

| Área | Estado |
|---|---|
| Autenticación JWT + bcrypt + blocklist | ✅ Completa |
| RBAC (3 roles: admin, leader, user) | ✅ Completa |
| Seed automático de roles/admin | ✅ Completa |
| CRUD Comunidades | ✅ Completa |
| Módulo Eventos (CRUD + aprobación + inscripciones) | ✅ Completa |
| Notificaciones in-app | ✅ Completa |
| Email de confirmación de inscripción | ✅ Completa |
| Subida de imágenes (Cloudinary) | ✅ Completa |
| Métricas admin y líder | ✅ Completa |
| Panel Admin (UI) | ✅ En uso |
| Panel Leader (UI) | ✅ En uso |
| Panel User (UI) | ✅ En uso |
| Landing page pública | ✅ Completa |

---

## Equipo

Proyecto desarrollado como trabajo de grado para el **SENA — Tecnólogo en Análisis y Desarrollo de Software**
Ficha **2995403**
