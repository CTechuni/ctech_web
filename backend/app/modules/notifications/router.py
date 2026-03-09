from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.auth.service import get_current_active_user
from . import service, schemas
from typing import List

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("/", response_model=List[schemas.NotificationResponse])
def get_notifications(db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    # Restringir a admin si es necesario, por ahora cualquier usuario autenticado puede verlas
    # pero el frontend admin solo las consumirá en el panel correspondiente.
    return service.list_notifications(db)

@router.patch("/{id}/read", response_model=schemas.NotificationResponse)
def mark_as_read(id: int, db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    return service.mark_as_read(db, id)

@router.post("/read-all")
def mark_all_as_read(db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    service.mark_all_as_read(db)
    return {"message": "Todas las notificaciones marcadas como leídas"}
