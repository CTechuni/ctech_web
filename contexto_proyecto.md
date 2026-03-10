# Contexto del Proyecto: CTech

## 📌 Visión General
**CTech** es una plataforma integral diseñada para potenciar y gestionar las **comunidades tecnológicas de Colombia**. El proyecto nace con la misión de centralizar el ecosistema tech nacional, conectando a entusiastas, desarrolladores, mentores y líderes de comunidad en un solo lugar.

Su propósito es facilitar el intercambio de conocimientos a través de mentorías y el acceso a recursos educativos, fortaleciendo el tejido tecnológico en el país.

---

## 🎯 Objetivos Actuales (Fase MVP)
1.  **Consolidación del Core**: Desarrollar el Producto Mínimo Viable (MVP) que permita el registro de usuarios y la gestión básica de perfiles.
2.  **Validación de Roles (RBAC)**: Implementar y verificar los permisos para los paneles de Administrador, Líder, Mentor y Usuario Estándar.
3.  **Gestión de Eventos**: Desplegar un sistema funcional de creación, edición y filtrado de eventos (Virtual/Presencial) sincronizado con un calendario global.
4.  **Estabilización API-Frontend**: Asegurar la integridad de datos y comunicación fluida entre el backend (FastAPI) y el frontend (Astro).

---

## 🛠️ Stack Tecnológico

### Frontend (Lado del Cliente)
*   **Framework**: [Astro 5.x](https://astro.build/) - Arquitectura de islas para máximo rendimiento.
*   **Lenguajes**: JavaScript (ES6+) y TypeScript.
*   **Estilos**: Vanilla CSS (Custom UI) y Bootstrap 5 para componentes estructurales.
*   **Iconografía**: FontAwesome 6.

### Backend (Lado del Servidor)
*   **Lenguaje**: Python 3.10+
*   **Framework**: FastAPI (Rápido, moderno y con documentación automática Swagger).
*   **ORM**: SQLAlchemy 2.0 para la gestión de modelos relacionales.
*   **Seguridad**: Autenticación con JWT (JSON Web Tokens) y control de acceso por roles.
*   **Multimedia**: Cloudinary API para gestión de imágenes.

### Base de Datos
*   **Motor**: PostgreSQL (Base de datos relacional robusta y escalable).

---

## ⚙️ Metodologías y Herramientas

### Metodología de Desarrollo
*   **Agile / Scrum**: Ciclos cortos de desarrollo enfocados en la entrega de valor inmediata (MVP).
*   **Arquitectura Modular**: Organización del código por módulos funcionales desacoplados.

### Herramientas
*   **Gestión de Código**: Git & GitHub.
*   **Entornos**: VS Code, Venv (Python), Node.js.
*   **Pruebas**: Scripts de validación automatizados y herramientas de consumo de API (Invoke-RestMethod/Curl).
