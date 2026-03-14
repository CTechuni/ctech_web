from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.auth.router import get_current_user
from app.modules.communities.models import Community
from . import service

router = APIRouter(prefix="/metrics", tags=["Metrics"])


@router.get("/admin")
def get_admin_metrics(db: Session = Depends(get_db), current=Depends(get_current_user)):
    if current.rol_id != 1:
        raise HTTPException(status_code=403, detail="Acceso restringido al administrador")
    return service.get_admin_dashboard(db)


@router.get("/community/{community_id}")
def get_community_metrics(community_id: int, db: Session = Depends(get_db), current=Depends(get_current_user)):
    # Solo admin o líder de la comunidad objetivo
    if current.rol_id == 1:
        # Admin puede ver métricas de cualquier comunidad, pero validamos que exista
        community = db.query(Community).filter(Community.id_community == community_id).first()
        if not community:
            raise HTTPException(status_code=404, detail="Comunidad no encontrada")
        return service.get_leader_dashboard(db, community_id)

    if current.rol_id == 3:
        # Líder solo puede ver métricas de su propia comunidad
        if not current.community_id or current.community_id != community_id:
            raise HTTPException(status_code=403, detail="No tienes permisos para ver métricas de esta comunidad")
        return service.get_leader_dashboard(db, community_id)

    # Otros roles no tienen acceso
    raise HTTPException(status_code=403, detail="No tienes permisos para ver métricas de comunidad")