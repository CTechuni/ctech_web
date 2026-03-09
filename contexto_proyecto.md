# Contexto del Proyecto: CTech

## 📌 Visión General
**CTech** es una plataforma integral de gestión para comunidades tecnológicas en Colombia. El proyecto nace como una solución para conectar a entusiastas de la tecnología, mentores y líderes de comunidad, facilitando la organización de eventos, el seguimiento de mentorías y el acceso a contenido educativo.

Este proyecto forma parte de la formación del **SENA (Ficha 2995403)** y busca estandarizar la interacción entre los diferentes actores del ecosistema tecnológico local.

---

## 🎯 Objetivos del Proyecto
1.  **Centralización**: Ofrecer un punto único para descubrir y registrarse en eventos tecnológicos.
2.  **Gestión de Mentorías**: Permitir que los usuarios soliciten y agenden sesiones 1-a-1 con mentores expertos.
3.  **Roles y Accesos (RBAC)**: Segmentar la experiencia según el perfil (Admin, Líder, Mentor, Usuario).
4.  **Seguimiento de Métricas**: Visualizar el impacto y crecimiento de las comunidades a través de dashboards interactivos.

---

## 🛠️ Stack Tecnológico

### Frontend (Lado del Cliente)
*   **Framework**: [Astro 5.x](https://astro.build/) - Utilizado para generar un sitio rápido, priorizando la entrega de HTML estático con islas de interactividad.
*   **Lenguajes**: JavaScript (ES6+) y TypeScript (para tipado y robustez).
*   **Estilos**: 
    *   **Vanilla CSS**: Diseño premium personalizado mediante variables CSS y componentes modulares.
    *   **Bootstrap 5**: Utilizado puntualmente para estructuras base y componentes de apoyo.
*   **Iconografía**: FontAwesome 6 (iconos sólidos y regulares).
*   **UI/UX**: Enfoque en accesibilidad, diseño responsivo y estética moderna (Glassmorphism, Dark Mode).

### Backend (Lado del Servidor)
*   **Lenguaje**: [Python 3.10+](https://www.python.org/)
*   **Framework**: [FastAPI](https://fastapi.tiangolo.com/) - Utilizado por su alto rendimiento, validación automática con Pydantic y generación automática de documentación de API (Swagger).
*   **ORM**: SQLAlchemy 2.0 - Para la gestión de modelos y consultas a la base de datos de manera eficiente.
*   **Seguridad**: OAuth2 con tokens JWT (JSON Web Tokens) para autenticación y autorización segura.
*   **Almacenamiento de Imágenes**: Cloudinary API - Gestión externa de activos multimedia.

### Base de Datos
*   **Motor**: [PostgreSQL](https://www.postgresql.org/) - Base de datos relacional robusta elegida por su escalabilidad e integridad de datos.

---

## ⚙️ Metodologías y Herramientas

### Metodología de Trabajo
*   **Agile / Scrum**: Desarrollo iterativo e incremental por sprints, priorizando el valor entregado al usuario final y la mejora continua.
*   **Diseño de Arquitectura**: 
    *   **Frontend**: Basado en Componentes Compartidos (`CalendarShared`, sidebar dinámico).
    *   **Backend**: Arquitectura modular por carpetas (auth, events, communities, etc.).

### Herramientas de Desarrollo
*   **Control de Versiones**: Git & GitHub.
*   **Gestión de Dependencias**: 
    *   Frontend: `npm` / `package.json`.
    *   Backend: `pip` / `requirements.txt`.
*   **Entorno**: Visual Studio Code con extensiones para Astro y Python.
*   **API Testing**: Invoke-RestMethod (PowerShell) y scripts personalizados de verificación.

---

## 🚀 A donde queremos llegar
El objetivo final es consolidar a **CTech** como la plataforma líder para comunidades SENA y externas en Colombia, logrando una automatización total de los certificados de asistencia, integraciones con calendarios externos (Google/Outlook) y un sistema de gamificación para incentivar la participación estudiantil.
