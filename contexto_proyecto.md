# Contexto del Proyecto: CTech

## Visión General
**CTech** es una plataforma diseñada para gestionar **comunidades tecnológicas de Colombia**. El proyecto centraliza la organización de comunidades tech, conectando a sus miembros a través de **eventos** coordinados por líderes y administradores.

Su propósito es facilitar el acceso, la inscripción y la comunicación entre miembros de comunidades tecnológicas bajo un sistema organizado por roles.

---

## Objetivos Actuales (Fase MVP)

1. **Gestión de comunidades** — Creación y administración de comunidades tecnológicas con líder asignado y código de acceso único.
2. **Sistema de eventos** — Flujo completo de creación, aprobación, publicación e inscripción a eventos (presenciales y virtuales).
3. **RBAC (3 roles)** — Permisos diferenciados para Admin, Líder y Usuario.
4. **Notificaciones y comunicación** — Notificaciones in-app y correos automáticos en inscripciones y cambios de estado.
5. **Métricas** — Dashboards con estadísticas para administradores y líderes.

---

## Roles del Sistema

| Rol | rol_id | Descripción |
|---|---|---|
| **admin** | 1 | Acceso total. Gestiona usuarios, comunidades y todos los eventos. |
| **leader** | 3 | Gestiona su comunidad: aprueba/rechaza eventos, ve miembros e inscripciones. |
| **user** | 4 | Se registra en eventos, recibe notificaciones, gestiona su perfil. |

> El rol **mentor** fue eliminado. CTech no tiene mentoría ni cursos.

---

## Stack Tecnológico

### Frontend
- **Framework**: Astro 5.x — arquitectura de islas.
- **Lenguajes**: JavaScript (ES6+) y TypeScript.
- **Estilos**: Bootstrap 5 + CSS personalizado.
- **Iconografía**: FontAwesome 6.5.

### Backend
- **Lenguaje**: Python 3.11+
- **Framework**: FastAPI con documentación automática Swagger (`/docs`).
- **ORM**: SQLAlchemy 2.0 — patrón de 4 capas: models → schemas → repository → service → router.
- **Autenticación**: JWT (python-jose, HS256) + bcrypt + token blocklist.
- **Email**: Gmail + Jinja2 templates.
- **Imágenes**: Cloudinary API.

### Base de Datos
- **Motor**: PostgreSQL 15+
- **Tablas activas**: `users`, `roles`, `profiles`, `communities`, `events`, `event_registrations`, `notifications`, `token_blocklist`.

---

## Módulos del Backend (`/api/v1/`)

| Módulo | Estado | Descripción |
|---|---|---|
| `auth` | ✅ Completo | Login, registro, logout, reset de contraseña |
| `users` | ✅ Completo | CRUD usuarios, cambio de rol, perfil |
| `communities` | ✅ Completo | CRUD comunidades, logo |
| `events` | ✅ Completo | CRUD + flujo aprobación + inscripciones + notificaciones |
| `metrics` | ✅ Completo | Dashboard admin y líder |
| `notifications` | ✅ Completo | Notificaciones in-app |
| `admin` | ✅ Completo | Panel admin |

**Módulos eliminados**: courses, sessions, specialties, technologies, content — no forman parte del alcance actual.

---

## Flujo de Eventos

```
Creación → draft/pending → approved | rejected
```

- **Líder / Admin**: el evento se aprueba automáticamente al crearlo.
- **Aprobación manual**: líder aprueba/rechaza eventos de su comunidad; admin aprueba cualquiera.
- **Visibilidad**: `publico` (visible sin auth) | `privado` (solo miembros de la comunidad).
- **Inscripción**: valida capacidad, duplicados y que el evento esté aprobado. Envía email + notificación.
- **`registered_count`**: incluido en cada respuesta de evento (subconsulta, sin N+1 queries).

---

## Metodologías y Herramientas

- **Agile / Scrum**: ciclos cortos enfocados en entrega del MVP.
- **Arquitectura modular**: módulos funcionales desacoplados.
- **Control de versiones**: Git & GitHub (rama principal: `main`, desarrollo en `vers33`).
- **Entornos**: VS Code, Venv (Python), Node.js.
- **Documentación API**: Swagger UI en `http://localhost:8000/docs`.
