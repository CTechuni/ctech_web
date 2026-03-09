from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, SessionLocal
from app.db.base_api import Base  # Importante: Base desde base_api para cargar todos los modelos
from app.db.init_db import seed_data # Para crear los roles y el admin automáticamente

# Importación de Routers
from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as users_router
from app.modules.communities.router import router as communities_router
from app.modules.content.router import router as content_router
from app.modules.courses.router import router as courses_router
from app.modules.events.router import router as events_router
from app.modules.mentoring_sessions.router import router as mentoring_router
from app.modules.metrics.router import router as metrics_router
from app.modules.specialties.router import router as specialties_router
from app.modules.technologies.router import router as technologies_router
from app.modules.admin.router import router as admin_router
from app.modules.notifications.router import router as notifications_router

# 1. Crear las tablas en PostgreSQL (basado en base_api.py)
Base.metadata.create_all(bind=engine)

# 2. Ejecutar el sembrado de datos iniciales (Comentado para evitar bloqueos en el arranque)
# db = SessionLocal()
# try:
#     seed_data(db)
# finally:
#     db.close()

app = FastAPI(
    title="CTech API",
    description="Plataforma LMS para comunidades tecnológicas en Colombia",
    version="1.0.0"
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex="https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_prefix = "/api/v1"

# Registro de Rutas
app.include_router(auth_router, prefix=f"{api_prefix}/auth", tags=["Auth"])
app.include_router(users_router, prefix=api_prefix)
app.include_router(communities_router, prefix=api_prefix)
app.include_router(content_router, prefix=api_prefix)
app.include_router(courses_router, prefix=api_prefix)
app.include_router(events_router, prefix=api_prefix)
app.include_router(mentoring_router, prefix=api_prefix)
app.include_router(metrics_router, prefix=api_prefix)
app.include_router(specialties_router, prefix=api_prefix)
app.include_router(technologies_router, prefix=api_prefix)
app.include_router(admin_router, prefix=api_prefix)
app.include_router(notifications_router, prefix=api_prefix)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bienvenido a CTech API - Proyecto SENA Ficha 2995403"}
 
