from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.auth.router import get_current_user
from . import service

router = APIRouter(prefix="/metrics", tags=["Metrics"])

@router.get("/admin") # Coincide exactamente con tu Swagger
def get_admin_metrics(db: Session = Depends(get_db), current=Depends(get_current_user)):
    # Solo accesible con token (candado en la imagen)
    return service.get_admin_dashboard(db)

@router.get("/community/{community_id}")
def get_community_metrics(community_id: int, db: Session = Depends(get_db), current=Depends(get_current_user)):
    return service.get_leader_dashboard(db, community_id)