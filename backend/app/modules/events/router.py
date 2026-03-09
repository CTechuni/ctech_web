from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.auth.router import get_current_user
from . import schemas, service

router = APIRouter(prefix="/events", tags=["Events"])

@router.get("/", response_model=list[schemas.EventResponse])
def get_events(db: Session = Depends(get_db)):
    return service.list_events(db)

@router.get("/upcoming", response_model=list[schemas.EventResponse])
def get_upcoming_events(db: Session = Depends(get_db)):
    return service.get_upcoming_events(db, limit=5)

@router.post("/", response_model=schemas.EventResponse)
def create_event(data: schemas.EventCreate, db: Session = Depends(get_db), current=Depends(get_current_user)):
    return service.create_event(db, data)

@router.post("/{event_id}/register")
def register_to_event(event_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current=Depends(get_current_user)):
    # 1. Obtener datos del evento y usuario
    from .models import Event
    from app.modules.users.models import User
    
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
        
    user = db.query(User).filter(User.id == current.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # 2. Enviar Email de Confirmación (Background Task)
    from app.core.email_service import email_service
    from app.modules.communities.models import Community
    
    community = db.query(Community).filter(Community.id_community == event.community_id).first()
    
    background_tasks.add_task(
        email_service.send_event_registration_email,
        recipient_email=user.email,
        name_user=user.name_user,
        event_name=event.title,
        event_date=str(event.event_date),
        event_time=str(event.event_time) if event.event_time else "Por definir",
        event_type=event.event_type or "Virtual",
        name_community=community.name_community if community else "CTech"
    )

    return {"message": "Registro exitoso", "event_title": event.title}

@router.delete("/{event_id}")
def delete_event(event_id: int, db: Session = Depends(get_db), current=Depends(get_current_user)):
    # Solo administradores pueden borrar
    if current.role != "admin":
        raise HTTPException(status_code=403, detail="No tienes permisos para borrar eventos")
        
    success = service.delete_event(db, event_id)
    if not success:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    return {"message": "Evento eliminado correctamente"}
