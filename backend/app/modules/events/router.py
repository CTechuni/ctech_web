from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, File, UploadFile
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.auth.router import get_current_user
from . import schemas, service, repository

router = APIRouter(prefix="/events", tags=["Events"])

# Auth opcional: devuelve el usuario si hay token, None si no hay
_optional_bearer = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", auto_error=False)

def get_optional_user(token: str = Depends(_optional_bearer), db: Session = Depends(get_db)):
    if not token:
        return None
    try:
        return get_current_user(token=token, db=db)
    except Exception:
        return None

# ── GET /events/ ──────────────────────────────────────────────────────────────
# Sin auth        → solo aprobados + públicos
# Autenticado(4)  → solo aprobados (ambas visibilidades)
# Líder(3)        → todos los de su comunidad
# Admin(1)        → todos
@router.get("/", response_model=list[schemas.EventResponse])
def get_events(db: Session = Depends(get_db), current=Depends(get_optional_user)):
    if current is None:
        return service.list_approved_public(db)
    if current.rol_id == 1:
        return service.list_all(db)
    if current.rol_id == 3:
        return service.list_by_community(db, current.community_id)
    return service.list_approved(db)



# ── GET /events/pending ───────────────────────────────────────────────────────
# Líder: ve eventos pendientes de su comunidad; Admin: todos los pendientes
@router.get("/pending", response_model=list[schemas.EventResponse])
def get_pending_events(db: Session = Depends(get_db), current=Depends(get_current_user)):
    if current.rol_id not in [1, 3]:
        raise HTTPException(status_code=403, detail="Solo líder o admin")
    if current.rol_id == 1:
        return service.list_all(db)  # admin ve todo
    return service.list_pending_by_community(db, current.community_id)

# ── GET próximos eventos ───────────────────────────────────────────────────────
@router.get("/upcoming", response_model=list[schemas.EventResponse])
def get_upcoming_events(db: Session = Depends(get_db), current=Depends(get_optional_user)):
    public_only = current is None
    return service.get_upcoming_events(db, limit=5, public_only=public_only)

# ── POST subir imagen de evento ────────────────────────────────────────────────
@router.post("/upload-image")
async def upload_event_image(file: UploadFile = File(...), current=Depends(get_current_user)):
    from app.core.cloudinary_service import upload_image
    if current.rol_id not in [1, 3]:
        raise HTTPException(status_code=403, detail="No tienes permisos para subir imágenes")
    url = upload_image(file.file, folder="events")
    if not url:
        raise HTTPException(status_code=500, detail="Error al subir la imagen a Cloudinary")
    return {"url": url}

# ── POST crear evento ──────────────────────────────────────────────────────────
# Admin(1), líder(3), pueden crear eventos
# líder se auto-asignan a su comunidad
# Líder: evento se aprueba automáticamente
@router.post("/", response_model=schemas.EventResponse)
def create_event(data: schemas.EventCreate, db: Session = Depends(get_db), current=Depends(get_current_user)):
    if current.rol_id == 3:
        data = data.model_copy(update={"community_id": current.community_id})

    # Líder y admin: el evento se aprueba automáticamente
    auto_approve = current.rol_id in [1, 3]
    event = service.create_event(db, data, auto_approve=auto_approve)
    
    # Notificación para administradores o líderes
    from app.modules.notifications.service import add_notification
    if not auto_approve:
        add_notification(db, "Nuevo Evento Pendiente", f"Se ha creado un evento que requiere aprobación: {event.title}", "warning")
    else:
        # Notificar a la comunidad (podría ser opcional, por ahora solo info)
        pass
        
    return event

# ── PUT editar evento ──────────────────────────────────────────────────────────
# Líder/admin pueden editar cualquier evento de su comunidad
@router.put("/{event_id}", response_model=schemas.EventResponse)
def update_event(event_id: int, data: schemas.EventUpdate, db: Session = Depends(get_db), current=Depends(get_current_user)):
    if current.rol_id not in [1, 3]:
        raise HTTPException(status_code=403, detail="No tienes permisos para editar eventos")

    event = repository.get_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    if current.rol_id == 3:
        # Líder: solo eventos de su comunidad
        if event.community_id != current.community_id:
            raise HTTPException(status_code=403, detail="Solo puedes editar eventos de tu comunidad")

    return repository.update(db, event_id, data.model_dump(exclude_unset=True))

# ── PATCH aprobar evento ───────────────────────────────────────────────────────
@router.patch("/{event_id}/approve", response_model=schemas.EventResponse)
def approve_event(event_id: int, db: Session = Depends(get_db), current=Depends(get_current_user)):
    if current.rol_id not in [1, 3]:
        raise HTTPException(status_code=403, detail="Solo líder o admin puede aprobar eventos")

    event = repository.get_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    if current.rol_id == 3 and event.community_id != current.community_id:
        raise HTTPException(status_code=403, detail="Solo puedes aprobar eventos de tu comunidad")

    return service.approve_event(db, event_id)

# ── PATCH rechazar evento ──────────────────────────────────────────────────────
@router.patch("/{event_id}/reject", response_model=schemas.EventResponse)
def reject_event(event_id: int, db: Session = Depends(get_db), current=Depends(get_current_user)):
    if current.rol_id not in [1, 3]:
        raise HTTPException(status_code=403, detail="Solo líder o admin puede rechazar eventos")

    event = repository.get_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    if current.rol_id == 3 and event.community_id != current.community_id:
        raise HTTPException(status_code=403, detail="Solo puedes rechazar eventos de tu comunidad")

    return service.reject_event(db, event_id)

# ── POST registrarse a un evento ──────────────────────────────────────────────
@router.post("/{event_id}/register")
def register_to_event(event_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current=Depends(get_current_user)):
    from app.modules.users.models import User
    from app.modules.communities.models import Community

    event = repository.get_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    user = db.query(User).filter(User.id == current.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    from app.core.email_service import email_service
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
    # Notificar al líder de la comunidad
    if community and community.leader_id:
        from app.modules.notifications.service import add_notification
        add_notification(
            db, 
            "Nueva Inscripción", 
            f"Un usuario se ha registrado en tu evento: {event.title}", 
            "event", 
            recipient_id=community.leader_id
        )

    return {"message": "Registro exitoso", "event_title": event.title}

# ── DELETE eliminar evento ─────────────────────────────────────────────────────
@router.delete("/{event_id}")
def delete_event(event_id: int, db: Session = Depends(get_db), current=Depends(get_current_user)):
    if current.rol_id not in [1, 3]:
        raise HTTPException(status_code=403, detail="No tienes permisos para eliminar eventos")

    event = repository.get_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")



    if current.rol_id == 3:
        if event.community_id != current.community_id:
            raise HTTPException(status_code=403, detail="Solo puedes eliminar eventos de tu comunidad")

    service.delete_event(db, event_id)
    return {"message": "Evento eliminado correctamente"}
