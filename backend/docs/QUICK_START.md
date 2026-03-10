# Quick Start Guide - Setup Local para Desarrollo

## ⚡ Setup Rápido (5 minutos)

### 1. Preparar Entorno

```bash
# Navegar al backend
cd backend

# Crear virtual environment
python -m venv .venv

# Activar virtual environment
. .venv/bin/activate  # Linux/Mac
# o
.venv\Scripts\Activate.ps1  # Windows PowerShell
```

### 2. Instalar Dependencias

```bash
# Instalar requirements
pip install -r requirements.txt

# (Opcional para producción) Instalar Gunicorn
pip install gunicorn
```

### 3. Configurar .env

```bash
# Copiar template
cp .env.example .env

# Editar .env con valores locales
# Para desarrollo, puedes usar valores simples:
ENVIRONMENT=development
DEBUG=True
JWT_SECRET_KEY=your-dev-secret-key-here
ADMIN_PASSWORD=admin123
```

**Ejemplo de .env para desarrollo local:**

```env
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ctech_dev

JWT_SECRET_KEY=dev-secret-key-abc123xyz
ADMIN_PASSWORD=admin123

CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

ADMIN_EMAIL=admin@localhost.local
ENVIRONMENT=development
DEBUG=True
ALLOWED_ORIGINS=http://localhost:4321,http://localhost:3000
```

### 4. Crear Base de Datos (PostgreSQL)

```bash
# Conectar a PostgreSQL
psql -U postgres

# Crear BD
CREATE DATABASE ctech_dev;
\q
```

### 5. Iniciar Servidor

```bash
# Desarrollo con auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# O con Gunicorn (simular producción)
gunicorn app.main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --reload
```

### 6. Verificar Instalación

```bash
# Health check
curl http://localhost:8000/health

# Ver documentación
# Abrir en navegador: http://localhost:8000/docs
```

---

## 🧪 Comandos Útiles

### Ver logs en vivo
```bash
tail -f logs/app.log
```

### Ejecutar tests
```bash
pytest tests/ -v
```

### Formatear código
```bash
# Instalar formato tools
pip install black flake8

# Formatear
black app/

# Lint
flake8 app/
```

### Crear admin user manualmente
```python
# python
python -c "
from app.core.database import SessionLocal
from app.modules.users.models import Role, User
from app.core.security import get_password_hash

db = SessionLocal()
admin_role = db.query(Role).filter_by(name_rol='admin').first()
admin = User(
    name_user='Admin Test',
    email='admin@test.local',
    password_hash=get_password_hash('admin123'),
    rol_id=admin_role.id_rol,
    status='active',
    is_email_verified=True
)
db.add(admin)
db.commit()
print('Admin created: admin@test.local / admin123')
"
```

---

## 📚 Documentación Importante

Después de setup, lee:
1. `SECURITY_CHECKLIST.md` - Seguridad y validaciones
2. `BUSINESS_LOGIC_IMPROVEMENTS.md` - Cambios de lógica
3. `PRODUCTION_DEPLOYMENT.md` - Para desplegar a prod
4. `AUDIT_SUMMARY.md` - Resumen de cambios

---

## ❓ Troubleshooting

### Problema: "ModuleNotFoundError: No module named 'app'"
**Solución:** Ejecutar desde directorio `backend/`:
```bash
cd backend
python -m uvicorn app.main:app --reload
```

### Problema: "Database connection refused"
**Verificar PostgreSQL está corriendo:**
```bash
# Mac
brew services list | grep postgres

# Linux
systemctl status postgresql

# Windows
# Abrir pgAdmin o verificar Services
```

### Problema: "JWT_SECRET_KEY no está configurado"
**Solución:** Crear `.env` desde `.env.example`:
```bash
cp .env.example .env
# Editar .env y agregar JWT_SECRET_KEY
```

### Problema: "Port 8000 already in use"
**Solución:** Usar puerto diferente:
```bash
uvicorn app.main:app --reload --port 8001
```

---

## 🔗 URLs Útiles (Desarrollo)

- **API Docs (Swagger):** http://localhost:8000/docs
- **API Docs (ReDoc):** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json
- **Health Check:** http://localhost:8000/health
- **Frontend:** http://localhost:4321

---

## 🎓 Primeros Pasos

### 1. Registrar usuario
```bash
curl -X POST http://localhost:8000/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@test.local",
    "name_user": "Test User",
    "password": "password123"
  }'
```

### 2. Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@test.local",
    "password": "password123"
  }'
```

### 3. Usar token para acceder a endpoints protegidos
```bash
# Usar el token del response anterior
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN"
```

---

## 📋 Checklist de Setup

- [ ] Virtual environment creado y activado
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] `.env` creado con valores correctos
- [ ] PostgreSQL instalado y corriendo
- [ ] Base de datos `ctech_dev` creada
- [ ] Servidor inicia sin errores
- [ ] `/health` endpoint responde
- [ ] `/docs` carga documentación Swagger
- [ ] Puedo hacer registro y login successfully

---

## 💡 Tips de Desarrollo

1. **Auto-reload activado:** Los cambios se recargan automáticamente
2. **Debugger:** Usa `breakpoint()` en código
3. **Tests:** Ejecuta `pytest -v` antes de commit
4. **Logging:** Los logs van a `logs/app.log`
5. **IDE**: Usa PyCharm o VS Code con Python extension

---

## 🚀 Estado de la Aplicación

Después de setup exitoso, deberías ver:

```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

Y en logs:

```
2026-03-03 12:30:45 - ctech_api - INFO - Database engine created for development environment
2026-03-03 12:30:45 - ctech_api - INFO - Database initialized successfully
2026-03-03 12:30:45 - ctech_api - INFO - Application starting up in development mode
2026-03-03 12:30:45 - ctech_api - INFO - Database is empty, seeding initial data...
2026-03-03 12:30:46 - ctech_api - INFO - ✅ Roles seeded successfully
2026-03-03 12:30:46 - ctech_api - INFO - ✅ Admin user seeded successfully: admin@localhost.local
```

---

**¡Setup completo! 🎉 Listo para desarrollar**
