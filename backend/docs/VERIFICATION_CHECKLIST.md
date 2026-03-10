# ✅ POST-AUDIT VERIFICATION CHECKLIST

Use este checklist para verificar que todos los cambios están en lugar y funcionan correctamente.

---

## 🔒 SEGURIDAD

### Credenciales
- [ ] `config.py` no contiene hardcoded secrets
- [ ] `JWT_SECRET_KEY` viene de `.env`
- [ ] `ADMIN_PASSWORD` viene de `.env`
- [ ] `.env` está en `.gitignore`
- [ ] `.env.example` tiene estructura correcta

### Contraseñas
- [ ] `security.py` no tiene fallback plaintext
- [ ] Bcrypt es el único algoritmo usado
- [ ] `password_hash` field es `String(255)`
- [ ] No hay comparaciones directas de strings

### Debug
- [ ] No hay `print()` statements en production code
- [ ] `logger` se usa en lugar de `print()`
- [ ] Logs van a archivo (no stdout en prod)
- [ ] DEBUG flag controla verbosidad de logs

### Tokens
- [ ] Tokens tienen claim `exp`
- [ ] `ACCESS_TOKEN_EXPIRE_MINUTES` está configurado
- [ ] Tokens se validan en `get_current_user()`
- [ ] Tokens expirados son rechazados

---

## 🌐 API

### CORS
- [ ] `allow_methods` es lista explícita (no "*")
- [ ] `allow_headers` es lista explícita (no "*")
- [ ] `ALLOWED_ORIGINS` viene de `.env`
- [ ] `max_age` está configurado (600s)

### Endpoints
- [ ] `/health` responde sin auth
- [ ] `/docs` deshabilitado si DEBUG=False
- [ ] `/redoc` deshabilitado si DEBUG=False
- [ ] `/openapi.json` deshabilitado si DEBUG=False

### Error Handling
- [ ] Global exception handler existe
- [ ] En producción no expone detalles internos
- [ ] En desarrollo muestra errores completos
- [ ] Todos los HTTP status codes son correctos

---

## 👥 AUTENTICACIÓN

### Login
- [ ] Valida email y password
- [ ] Verifica `user.status == "active"`
- [ ] Rechaza usuarios inactivos
- [ ] Devuelve token con expiración

### Logout
- [ ] Coloca token en blacklist
- [ ] Siguiente uso del token es rechazado

### Autorización
- [ ] `/users/` lista requiere role=admin
- [ ] `/users/{id}/promote` requiere role=admin
- [ ] `/users/{id}/delete` requiere role=admin
- [ ] `/users/{id}/delete` no permite self-delete

---

## 📝 USUARIOS

### Registro
- [ ] Email debe ser único
- [ ] Password es hashed, no plaintext
- [ ] Usuario obtiene role "user" por defecto
- [ ] User creado con `status="active"`

### Perfil
- [ ] `/users/me` devuelve usuario actual
- [ ] `/users/me` requiere autenticación
- [ ] `/users/{id}/promote` requiere specialty_id
- [ ] Solo admins pueden cambiar roles

### Eliminación
- [ ] `/users/{id}` solo funciona para admin
- [ ] Admin no puede eliminarse a sí mismo
- [ ] El usuario se elimina correctamente

---

## 🎉 EVENTOS

### Creación
- [ ] Requiere autenticación
- [ ] `created_by` se asigna al usuario actual
- [ ] `capacity` debe ser > 0
- [ ] `date_events` no puede ser pasado

### Upload
- [ ] Solo tipos MIME permitidos
- [ ] Rechaza tipos inválidos (PHP, exe, etc.)
- [ ] Archivo se sube a Cloudinary
- [ ] URL se devuelve correctamente

### Actualización
- [ ] Solo creador o admin pueden actualizar
- [ ] Otros usuarios reciben 403
- [ ] Cambios se guardan en BD

### Eliminación
- [ ] Solo creador o admin pueden eliminar
- [ ] Otros usuarios reciben 403
- [ ] Evento se elimina de BD

---

## 🗄️ BASE DE DATOS

### Modelos
- [ ] `User.password_hash` es `String(255)`
- [ ] `User` tiene `registration_date`
- [ ] `User` tiene `last_login`
- [ ] `User` tiene `is_email_verified`
- [ ] `User` tiene `status` (indexed)

### Seed Data
- [ ] Se ejecuta solo una vez
- [ ] Roles se crean correctamente
- [ ] Admin se crea solo si no existe
- [ ] BD vacía al iniciar, solo llena una vez

### Migrations
- [ ] Se pueden ejecutar migraciones
- [ ] Cambios al schema se guardan
- [ ] Versión anterior sigue siendo compatible

---

## 📊 LOGGING

### Logger
- [ ] `logger.py` existe y funciona
- [ ] `logs/app.log` se crea
- [ ] Logs rotan por tamaño
- [ ] Logs incluyen DateTime

### Niveles
- [ ] `DEBUG` nivel en desarrollo
- [ ] `INFO` nivel en producción
- [ ] Eventos importantes se registran
- [ ] Accesos no autorizados se registran

### Módulos
- [ ] `logging.getLogger("ctech_api.auth")`
- [ ] `logging.getLogger("ctech_api.security")`
- [ ] `logging.getLogger("ctech_api.users")`
- [ ] `logging.getLogger("ctech_api.database")`

---

## 📧 RESETEAR CONTRASEÑA

### Forgot Password
- [ ] Endpoint existe en `/auth/forgot-password`
- [ ] Devuelve mensaje genérico
- [ ] No revela si email existe
- [ ] Token se genera internamente

### Reset Password
- [ ] Endpoint existe en `/auth/reset-password`
- [ ] Requiere token válido
- [ ] Requiere password nueva
- [ ] Valida expiración del token
- [ ] Nueva contraseña se hashea
- [ ] Token se invalidar después de uso

---

## 🚀 CONFIGURACIÓN

### Environment
- [ ] `ENVIRONMENT` puede ser dev/staging/prod
- [ ] `DEBUG` es boolean
- [ ] Todos los valores requeridos están en .env
- [ ] `.env` no está en git

### Variables
- [ ] `DB_*` configurado
- [ ] `JWT_*` configurado
- [ ] `CLOUDINARY_*` configurado
- [ ] `ADMIN_*` configurado

### Startup
- [ ] App inicia sin errores
- [ ] Seed data se ejecuta correctamente
- [ ] Logging inicializa
- [ ] BD se conecta exitosamente

---

## 🧪 TESTING

### Unit Tests
- [ ] Tests para `security.py` pasan
- [ ] Tests para `auth` pasan
- [ ] Tests para `users` pasan
- [ ] Tests para `events` pasan

### Integration Tests
- [ ] Login/logout flujo funciona
- [ ] CRUD operaciones funcionan
- [ ] Autorización funciona

### Security Tests
- [ ] User inactivo no puede login
- [ ] Admin no puede self-delete
- [ ] Token expirado es rechazado
- [ ] Autorización es validada

---

## 📈 PERFORMANCE

### Queries
- [ ] Índices en BD existen
- [ ] Queries eficientes
- [ ] N+1 queries evitadas

### Caching
- [ ] Response caching está configurado
- [ ] CORS caching está configurado

### Rate Limiting
- [ ] TODO: Implementar rate limiting
- [ ] TODO: Limitar logins fallidos
- [ ] TODO: Limitar password reset

---

## 🔍 VERIFICACIÓN MANUAL

### Pruebas en Postman/curl

```bash
# Health check
curl http://localhost:8000/health

# Registrar usuario
curl -X POST http://localhost:8000/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@local","name_user":"Test","password":"pass123"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@local","password":"pass123"}'

# Usar token
TOKEN="<from-login-response>"
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN"

# Verificar CORS
curl -i -X OPTIONS http://localhost:8000/api/v1/users/ \
  -H "Origin: http://localhost:4321"
```

---

## 📋 Antes de Deploy

### Final Checklist
- [ ] Todos los tests pasan
- [ ] No hay compiler warnings
- [ ] Código está formateado
- [ ] Documentación está actualizada
- [ ] Security scan completado
- [ ] Performance benchmarks OK
- [ ] Load testing completado
- [ ] Disaster recovery plan existe

### Setup del Servidor
- [ ] PostgreSQL instalado
- [ ] BD creada
- [ ] Usuario BD con permisos correctos
- [ ] Firewall configurado
- [ ] SSL/HTTPS configurado
- [ ] Backups automatizados
- [ ] Monitoreo activo

### Post Deploy
- [ ] Endpoints responden
- [ ] Logs se generan
- [ ] Alertas funcionan
- [ ] Backups funcionan
- [ ] Monitoring activo

---

## 🆘 Troubleshooting

Si algo no funciona, revisar:

1. **Auth falla**: Verificar JWT_SECRET_KEY en .env
2. **BD no conecta**: Verificar credenciales en .env
3. **Logs no se crean**: Verificar permisos en carpeta logs/
4. **CORS error**: Verificar ALLOWED_ORIGINS en .env
5. **Token invalid**: Verificar token no está expirado

---

## ✅ Estatus Final

Cuando todo esté verificado:

```
✅ Seguridad verificada
✅ Funcionalidad verificada
✅ Performance verificada
✅ Documentación verificada
✅ Listo para PRODUCCIÓN
```

**Fecha de Verificación:** _______________

**Verificado por:** _______________

**Aprobado para Deploy:** ☐ SÍ  ☐ NO (revisar observaciones)

**Observaciones:**
```
_________________________________________________
_________________________________________________
_________________________________________________
```

---

**¡Checklist Completado! 🎉**
