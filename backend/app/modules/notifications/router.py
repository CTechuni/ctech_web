from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.auth.service import get_current_active_user
from . import service, schemas
from typing import List

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("/", response_model=List[schemas.NotificationResponse])
def get_notifications(db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    is_admin = current_user.rol_id == 1
    return service.list_notifications(db, user_id=current_user.id, is_admin=is_admin)

@router.patch("/{id}/read", response_model=schemas.NotificationResponse)
def mark_as_read(id: int, db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    return service.mark_as_read(db, id, current_user.id)

@router.post("/read-all")
def mark_all_as_read(db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    service.mark_all_as_read(db, user_id=current_user.id)
    return {"message": "Todas las notificaciones marcadas como leídas"}
