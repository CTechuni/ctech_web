from fastapi import FastAPI
# Importaciones de los módulos recuperados
from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as users_router
from app.modules.communities.router import router as communities_router
from app.modules.mentoring.router import router as mentoring_router
from app.modules.events.router import router as events_router
from app.modules.technologies.router import router as tech_router
from app.modules.specialties.router import router as specialties_router
from app.modules.admin.router import router as admin_router

app = FastAPI(title="CTech API", version="1.0.0")

# Endpoint de Health (para que aparezca primero como en tus capturas)
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}

# Registro con prefijo /api/v1 (fundamental para que el Swagger coincida)
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(users_router, prefix="/api/v1/users", tags=["Users"])
app.include_router(communities_router, prefix="/api/v1/communities", tags=["Communities"])
app.include_router(mentoring_router, prefix="/api/v1/sessions", tags=["Mentoring Sessions"])
app.include_router(events_router, prefix="/api/v1/events", tags=["Events"])
app.include_router(tech_router, prefix="/api/v1/tech", tags=["Technologies"])
app.include_router(specialties_router, prefix="/api/v1/specialties", tags=["Specialties"])
app.include_router(admin_router, prefix="/api/v1/admin", tags=["Admin"])