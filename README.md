# CTech Platform 🚀

> **Plataforma LMS para comunidades tecnológicas en Colombia**
> Proyecto SENA — Ficha 2995403

---

## 📋 Descripción del Proyecto

CTech es una plataforma LMS **gratuita** dirigida exclusivamente a **comunidades tecnológicas en Colombia**. Su propósito es conectar a personas interesadas en aprender tecnología (nivel básico, intermedio y avanzado) con comunidades organizadas, proporcionándoles acceso a cursos, eventos y sesiones de mentoría de forma centralizada.

La plataforma no requiere pago alguno — el acceso es libre y el crecimiento de la comunidad se logra a través de **eventos públicos** y el **intercambio presencial del código de comunidad** por parte del líder.

---

## 🔑 Modelo de Funcionamiento

### 💡 Acceso Gratuito
La plataforma es **100% gratuita** para todos los usuarios. No hay costo de inscripción, membresía ni acceso a contenido.

### 🏘️ Comunidades Tecnológicas
CTech está dirigida a **comunidades de tecnología en Colombia**: grupos de personas interesadas en aprender y crecer en el área tech, organizadas por temática (desarrollo web, mobile, datos, ciberseguridad, etc.).

Cada comunidad tiene:
- Un **Líder** responsable de gestionar su comunidad dentro de la plataforma.
- Su propio catálogo de **cursos**, **eventos** y **contenido educativo**.
- Un **código de comunidad** único que funciona como llave de acceso.

### 📣 Promoción a través de Eventos Públicos
Las comunidades se promocionan mediante **eventos públicos** visibles para cualquier persona que visite la plataforma, **sin necesidad de registro**. Estos eventos:
- Funcionan como **vitrina de atracción** para personas interesadas en tecnología.
- Muestran **fichas informativas** con imágenes del lugar del evento (foto del sitio, dirección, fecha), diseñadas para generar interés y convocar asistentes.
- Permiten que los visitantes conozcan la comunidad antes de unirse formalmente.
- No exponen el contenido interno (cursos, mentorías) — solo la información pública del evento.

> 📸 En la vista de visitante se despliegan **fichas visuales** con imagen del lugar del evento, nombre, fecha y tipo (presencial / online), todo sin requerir cuenta.

### � Estados de los Eventos: Público vs Privado

Al igual que los cursos, los eventos tienen dos estados de visibilidad:

| Estado | Visibilidad | Acceso al detalle |
|---|---|---|
| 🌐 **Público** | Visible para cualquier visitante sin registro | Solo muestra la **ficha informativa**. Miembros de CTech reciben notificación al publicarse. |
| 🔒 **Privado** | Solo visible para miembros registrados de la comunidad | Acceso completo. Miembros de la comunidad reciben notificación al publicarse. |

**Reglas de acceso:**
- **Visitante (sin cuenta):** ve los eventos públicos como fichas visuales — sirven para atraer e informar, no para participar.
- **Usuario registrado con código de comunidad:** accede a **todos los eventos** de la comunidad (públicos y privados), con capacidad de inscribirse y ver todo el detalle.
- **Sistema proactivo**: El usuario recibe una notificación en su panel y un correo al confirmar su inscripción.

> 🔑 Los eventos públicos son la puerta de entrada. El acceso completo a inscripciones, detalles y recursos requiere ser miembro registrado de la comunidad.


### �🔐 Ingreso a una Comunidad por Código
El **Líder de comunidad** comparte de forma **presencial** (en los eventos o encuentros físicos) el **código único de su comunidad** a las personas interesadas. Con ese código, el usuario puede:
- Registrarse y unirse a esa comunidad específica.
- Acceder a todos sus **cursos**, **eventos internos** y **sesiones de mentoría**.
- Interactuar con otros miembros y mentores dentro del espacio privado de la comunidad.

> 🤝 El código NO se publica en la plataforma — se entrega en persona por el líder, asegurando que solo personas realmente interesadas y vetadas por la comunidad accedan al contenido privado.

### � Estados de los Cursos: Público vs Privado

Los cursos dentro de cada comunidad pueden tener dos estados de visibilidad:

| Estado | Visibilidad | Acceso al contenido |
|---|---|---|
| 🌐 **Público** | Visible en la vista de visitante (sin registro) | Solo se muestra la **ficha del curso** (título, descripción, nivel). El visitante **no accede al contenido completo** |
| 🔒 **Privado** | Solo visible para miembros registrados de la comunidad | Acceso completo a **lecciones, recursos, eventos y mentorías** de la comunidad |

**Reglas de acceso:**
- **Visitante (sin cuenta):** puede ver los cursos marcados como públicos y los eventos públicos, pero únicamente como vista previa. No puede acceder al contenido, lecciones ni interacciones.
- **Usuario registrado con código de comunidad:** accede a **todo el contenido** de esa comunidad — tanto cursos públicos y privados, como eventos internos, sesiones de mentoría y recursos educativos.

> 🔑 El acceso completo requiere registro + código de comunidad. Los cursos públicos son una herramienta de atracción; el valor real está en el ecosistema privado de la comunidad.

---

### �📚 Niveles de Aprendizaje
El contenido educativo de cada comunidad está organizado por nivel de dificultad:

| Nivel | Descripción |
|---|---|
| 🟢 **Básico** | Para personas que están comenzando en el área tech, sin experiencia previa |
| 🟡 **Intermedio** | Para quienes ya tienen fundamentos y quieren profundizar sus conocimientos |
| 🔴 **Avanzado** | Para profesionales que buscan especializarse en tecnologías y competencias de alto nivel |

---


## � Objetivo General

Desarrollar una plataforma LMS web que centralice la gestión del aprendizaje, la formación de comunidades tecnológicas y el intercambio de conocimiento entre personas interesadas en tecnología en **Colombia**, facilitando el acceso a cursos, eventos, mentorías y contenido educativo de calidad bajo un sistema organizado por roles.

---

## 📌 Objetivos Específicos

1. **Gestionar comunidades tecnológicas** — Permitir la creación, organización y administración de comunidades temáticas dentro de la plataforma.
2. **Centralizar la oferta de cursos y contenido** — Ofrecer un catálogo de cursos y materiales educativos accesibles para todos los usuarios registrados.
3. **Facilitar la mentoría** — Conectar a mentores con usuarios mediante la gestión de sesiones de mentoría programadas.
4. **Administrar eventos** — Registrar, publicar y gestionar eventos tecnológicos (presenciales y virtuales).
5. **Implementar control de acceso por roles (RBAC)** — Garantizar que cada tipo de usuario (Admin, Líder, Mentor, Usuario) tenga acceso únicamente a las funciones que le corresponden.
6. **Proveer métricas e indicadores** — Generar estadísticas sobre el uso de la plataforma para la toma de decisiones por parte de administradores y líderes.
7. **Asegurar la integridad y seguridad de los datos** — Proteger la información de los usuarios mediante autenticación JWT, hashing de contraseñas con bcrypt y validación de datos con Pydantic.

---

## 👥 Público Objetivo

| Perfil | Descripción |
|---|---|
| **Desarrolladores / Programadores** | Personas que buscan aprender nuevas tecnologías, certificarse o conectar con comunidades afines |
| **Estudiantes de tecnología** | Estudiantes de carreras técnicas, tecnológicas y profesionales en el área de sistemas e informática |
| **Líderes de comunidad tech** | Personas que organizan y dirigen comunidades tecnológicas locales o virtuales |
| **Mentores** | Profesionales con experiencia que desean compartir conocimiento a través de sesiones de mentoría |
| **Administrativos SENA / Instituciones** | Gestores que necesitan supervisar el desempeño y crecimiento de las comunidades |

> 🇨🇴 **País de aplicación: Colombia únicamente.**
> La plataforma está enfocada exclusivamente en el ecosistema tecnológico colombiano, priorizando comunidades, eventos y mentores del territorio nacional.

---

## �🏗️ Arquitectura General

```
CTech/
├── backend/       → API REST (FastAPI + PostgreSQL)
└── frontend/      → Interfaz web (Astro + Bootstrap 5)
```

La arquitectura es una **SPA híbrida desacoplada**:
- El **backend** expone una API REST en `/api/v1/`.
- El **frontend** consume la API mediante `fetch` nativo desde el cliente (JavaScript vanilla).
- La autenticación es **stateless via JWT**, almacenado en `localStorage` con soporte multi-sesión por rol.

---

## ⚙️ Stack Tecnológico

### Backend

| Tecnología | Versión | Rol |
|---|---|---|
| **Python** | 3.11+ | Lenguaje principal |
| **FastAPI** | última | Framework web / API REST |
| **Uvicorn** | última | Servidor ASGI |
| **SQLAlchemy** | última | ORM (mapeo objeto-relacional) |
| **PostgreSQL** | 15+ | Base de datos relacional |
| **psycopg2-binary** | última | Driver PostgreSQL para Python |
| **python-jose** | última | Generación y validación de JWT |
| **passlib (bcrypt)** | última | Hashing seguro de contraseñas |
| **Pydantic / pydantic-settings** | v2 | Validación de datos y settings |
| **python-dotenv** | última | Gestión de variables de entorno |
| **Cloudinary** | última | Almacenamiento y gestión de imágenes |

### Frontend

| Tecnología | Versión | Rol |
|---|---|---|
| **Astro** | 5.x | Framework SSG/SSR híbrido |
| **TypeScript** | 5.x | Tipado estático |
| **Bootstrap** | 5.3.x | Framework CSS de componentes |
| **JavaScript (ESM)** | ES2022 | Lógica de cliente (fetch, auth) |

---

## 🔐 Sistema de Autenticación y RBAC

- **JWT** con `python-jose` y algoritmo **HS256**. Token con expiración configurable (por defecto 1440 min / 24 h).
- **Hashing** de contraseñas con **bcrypt** usando `passlib`.
- **Multi-sesión por rol**: el frontend guarda tokens separados en `localStorage` con clave dinámica por rol (`ctech_token_admin`, `ctech_token_mentor`, etc.).
- **RBAC (Role-Based Access Control)**: 4 roles definidos en la BD:
  - `admin` — acceso total al sistema
  - `leader` — gestión de su comunidad
  - `mentor` — gestión de mentorías y contenido
  - `user` — acceso al catálogo y aprendizaje
- Las rutas del frontend validan el rol activo en cada carga de página mediante `auth.js`.
- El backend protege endpoints con dependencias FastAPI que extraen y verifican el token JWT del header `Authorization: Bearer`.
- **Seed automático**: al iniciar el backend, `init_db.py` crea los roles y el usuario administrador si no existen.

---

## 🗄️ Base de Datos

- **Motor**: PostgreSQL (conexión configurada por variables de entorno).
- **ORM**: SQLAlchemy con declarative base.
- **Migraciones**: directorio `migrations/` disponible.
- **Tablas principales** (generadas por los modelos de cada módulo):
  - `users`, `roles`
  - `communities`
  - `events`
  - `courses`
  - `mentoring_sessions`
  - `content`
  - `specialties`
  - `technologies`
  - `metrics`

---

## 📦 Módulos del Backend (`/api/v1/`)

| Módulo | Prefijo de Ruta | Descripción |
|---|---|---|
| **auth** | `/api/v1/auth` | Login, generación de token JWT |
| **users** | `/api/v1/users` | CRUD de usuarios y perfiles |
| **communities** | `/api/v1/communities` | Gestión de comunidades tecnológicas |
| **events** | `/api/v1/events` | Creación y consulta de eventos |
| **courses** | `/api/v1/courses` | Cursos y módulos de aprendizaje |
| **mentoring_sessions** | `/api/v1/mentoring_sessions` | Sesiones de mentoría |
| **content** | `/api/v1/content` | Contenido educativo / recursos |
| **metrics** | `/api/v1/metrics` | Indicadores y estadísticas |
| **specialties** | `/api/v1/specialties` | Especialidades técnicas |
| **technologies** | `/api/v1/technologies` | Catálogo de tecnologías |
| **admin** | `/api/v1/admin` | Operaciones exclusivas del administrador |

Cada módulo sigue la estructura:
```
módulo/
├── router.py    → Rutas FastAPI
├── models.py    → Modelos SQLAlchemy
├── schemas.py   → Schemas Pydantic
└── service.py   → Lógica de negocio (en algunos módulos)
```

---

## 🖥️ Estructura del Frontend

### Layouts por Rol

| Layout | Archivo | Uso |
|---|---|---|
| **AdminLayout** | `AdminLayout.astro` | Panel de administración |
| **LeaderLayout** | `LeaderLayout.astro` | Panel de líderes de comunidad |
| **MentorLayout** | `MentorLayout.astro` | Panel de mentores |
| **UserLayout** | `UserLayout.astro` | Panel del usuario aprendiz |
| **MainLayout** | `MainLayout.astro` | Páginas públicas (landing, login) |

### Páginas Implementadas

**Admin (`/admin`)**
- `index.astro` — Dashboard principal con KPIs y tablas
- `users.astro` — Gestión de usuarios
- `communities.astro` — Gestión de comunidades
- `courses.astro` — Gestión de cursos
- `events/` — Gestión de eventos
- `leaders.astro` — Gestión de líderes
- `mentors.astro` — Gestión de mentores
- `settings.astro` — Configuración del sistema
- `profile.astro` — Perfil del administrador
- `showcase.astro` — Vista de muestra de estilos

**Mentor (`/mentor`)**
- `index.astro` — Dashboard del mentor
- `sessions.astro`, `profile.astro`, `content.astro`

**Leader (`/leader`)**
- `index.astro` — Dashboard del líder
- `community.astro` — Vista de comunidad

**User (`/user`)**
- `index.astro` — Dashboard del usuario
- `courses.astro`, `events.astro`, `profile.astro`, `calendar.astro`

**Públicas**
- `index.astro` — Landing page
- `404.astro` — Página de error
- `terminos-y-condiciones.astro`

### Componentes

Los componentes están organizados por rol en `src/components/`:
- `admin/` — Sidebar, Header, modals, tablas
- `leader/` — Sidebar, Header específico
- `mentor/` — Sidebar, Header específico
- `user/` — Sidebar, Header específico
- `shared/` — Componentes reutilizables entre roles

### Utilidades del Cliente

| Archivo | Descripción |
|---|---|
| `utils/auth.js` | Gestión de sesiones JWT, validación de roles, redirección automática, multi-sesión |
| `utils/communities-logic.js` | Lógica de negocio del módulo comunidades (CRUD, formularios) |
| `utils/escape.js` | Helpers para sanitización de HTML |

---

## 📁 Estructura del Repositorio

```
CTech/
├── backend/
│   ├── app/
│   │   ├── core/          → config, database, security, logger, cloudinary
│   │   ├── db/            → base_api.py (Base SQLAlchemy), init_db.py (seed)
│   │   ├── modules/       → 11 módulos de negocio
│   │   ├── tests/         → pruebas
│   │   └── main.py        → entry point FastAPI
│   ├── migrations/
│   ├── requirements.txt
│   ├── .env               → variables de entorno (no commitear)
│   └── run_backend.bat    → script de inicio rápido (Windows)
│
├── frontend/
│   ├── src/
│   │   ├── components/    → componentes por rol
│   │   ├── layouts/       → layouts por rol
│   │   ├── pages/         → páginas por rol
│   │   ├── styles/        → estilos globales CSS
│   │   ├── utils/         → auth.js, lógica cliente
│   │   └── config/        → configuración de constantes (API URL, etc.)
│   ├── public/            → assets estáticos
│   ├── astro.config.mjs
│   └── package.json
│
├── database/              → scripts SQL adicionales
└── README.md
```

---

## 🚀 Cómo Levantar el Proyecto

### Backend

```bash
# 1. Crear entorno virtual
cd backend
python -m venv .venv
.venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
cp .env.example .env
# → Editar .env con credenciales de PostgreSQL, JWT secret y Cloudinary

# 4. Iniciar el servidor
uvicorn app.main:app --reload --port 8000
# O usar el script:
run_backend.bat
```

La API queda disponible en: `http://localhost:8000`
Documentación interactiva: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

La aplicación queda disponible en: `http://localhost:4321`

---

## 🌐 Variables de Entorno

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
```

### Frontend (`.env`)

```env
PUBLIC_API_URL=http://localhost:8000
```

---

## ✅ Estado del Proyecto

| Área | Estado |
|---|---|
| Estructura de módulos backend | ✅ Completa |
| Modelos de base de datos | ✅ Completa |
| Autenticación JWT + bcrypt | ✅ Completa |
| RBAC (4 roles) | ✅ Completa |
| Seed automático de roles/admin | ✅ Completa |
| Panel Admin (UI) | ✅ En uso |
| Panel Leader (UI) | ✅ En uso |
| Panel Mentor (UI) | ✅ En uso |
| Panel User (UI) | ✅ En uso |
| Landing page pública | ✅ Completa |
| Sistema multi-sesión frontend | ✅ Completa |
| Integración Cloudinary | ✅ Configurada |
| CRUD Comunidades (Admin) | ✅ Funcional |
| CRUD Líderes (edición parcial PATCH) | ✅ Funcional |
| Formularios con validación | ✅ Funcional |
| Pruebas (tests/) | 🔄 En progreso |

---

## 👥 Equipo

Proyecto desarrollado como trabajo de grado para el **SENA — Tecnólogo en Análisis y Desarrollo de Software**
Ficha **2995403**
