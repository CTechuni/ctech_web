# CTech — Contexto Técnico y Lógica de Negocio

> Este documento consolida la historia técnica, mejoras de seguridad y la evolución del sistema, enfocándose en la gestión centralizada de **Eventos** y **Comunidades**.

---

## 📊 Resumen de Evolución (Auditoría 2026)
Tras una auditoría profunda de seguridad y lógica, el sistema fue llevado a estándares de producción.

- **Fase de Limpieza**: Se eliminaron 5 módulos obsoletos (cursos, mentorías, etc.).
- **Seguridad Alcanzada**: ~85% de cumplimiento de estándares OWASP.
- **Cambios Estructurales**: +500 líneas modificadas para reforzar la validación de datos.

---

## 📅 El Enfoque en Eventos y Comunidades
Tras la desactivación de cursos y mentores, el backend se ha optimizado para priorizar la estabilidad:

### 1. Autorización Estricta
- **Lógica**: Se valida que solo los Líderes (rol 3) de la comunidad respectiva o los Administradores (rol 1) puedan gestionar eventos.
- **Seguridad**: Previene la edición cruzada de eventos entre distintas comunidades.

### 2. Validación de Datos en Eventos
- **Capacidad**: Verificación obligatoria de entero positivo (>0).
- **Imágenes**: Filtro estricto por tipo de archivo (`JPEG`, `PNG`, `WebP`) antes de procesar en Cloudinary.
- **Relaciones**: Se eliminó toda dependencia con `specialty_id` o `course_id` de los modelos de eventos.

---

## 🔒 Mejoras de Seguridad y Sesión

### 1. Gestión de Sesión Única (Multi-Pestaña)
Para evitar que un usuario manipule roles o sesiones en múltiples pestañas del navegador:
- **Backend**: El modelo `User` guarda `last_valid_token`. Cualquier token anterior es invalidado automáticamente ante un nuevo login.
- **Frontend**: Sincronización instantánea de logout/login entre pestañas usando `localStorage` y eventos de `storage`.

### 2. Fortalecimiento de Credenciales
- **Contraseñas**: Eliminación total de comparaciones en texto plano. Uso exclusivo de `bcrypt`.
- **Base de Datos**: El campo `password_hash` ahora soporta hasta 255 caracteres para máxima compatibilidad futura.
- **Secretos**: Remoción de todas las llaves hardcodeadas. Uso obligatorio de variables de entorno (`.env`).

---

### 3. Sincronización de Notificaciones Targeted
El sistema ha evolucionado de alertas globales a notificaciones inteligentes basadas en roles:
- **Liderazgo Informado**: El líder recibe notificaciones de "Nuevo Miembro" y "Inscripción en Evento" solo de su comunidad.
- **Confirmación al Usuario**: El usuario recibe una alerta de éxito al inscribirse, reforzando la interacción.
- **Aviso Masivo**: Se implementó una lógica de difusión para que nuevos eventos públicos alerten a toda la base de usuarios.

### 4. Vínculo Líder-Comunidad (Integridad)
Se garantiza la relación 1-a-1 mediante:
- **Sincronización en Cascada**: Al cambiar un líder en la tabla de comunidades, se actualiza automáticamente el perfil del usuario (rol y community_id).
- **Limpieza de Huérfanos**: La eliminación de un usuario líder limpia automáticamente la referencia en la comunidad para permitir una nueva asignación.

---

## 📁 Registro Técnico de Cambios por Archivo

| Componente | Archivo | Mejoras Aplicadas |
|---|---|---|
| **Core** | `config.py` | Variables de entorno requeridas, remoción de defaults inseguros. |
| **Auth** | `router.py` | Registro restringido a Rol 4; notificaciones dirigidas a líderes. |
| **Users** | `service.py` | Lógica de sincronización bi-directional Líder <-> Comunidad. |
| **Events** | `service.py` | Automatización de notificaciones por visibilidad (`publico`/`privado`). |
| **Notifications**| `models.py` | Adición de `recipient_id` para segmentación de alertas. |

---

## 🚀 Próximos Pasos Recomendados
1. **Refresh Tokens**: Implementar rotación periódica de tokens de acceso.
2. **Soft Deletes**: Implementar borrado lógico en `Users` y `Events` para historial.
3. **Paginación**: Estandarizar la paginación en todos los endpoints de lista con Pydantic.

---
*Este documento consolida y reemplaza: AUDIT_SUMMARY.md, BUSINESS_LOGIC_IMPROVEMENTS.md, MULTI_TAB_SESSION_MANAGEMENT.md, README_AUDIT.md y REFERENCE_GUIDE.md.*
