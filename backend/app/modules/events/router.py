from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, File, UploadFile, Query
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.auth.router import get_current_user
from . import schemas, service, repository
from app.modules.notifications.service import add_notification
from app.core.email_service import email_service
from app.modules.communities.models import Community
from app.modules.users.models import User
from app.core.cloudinary_service import upload_image
import io

router = APIRouter(prefix="/events", tags=["Events"])

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Auth opcional: devuelve el usuario si hay token válido, None si no
_auth_scheme = HTTPBearer(auto_error=False)

def get_optional_user(
    res: Optional[HTTPAuthorizationCredentials] = Depends(_auth_scheme), 
    db: Session = Depends(get_db)
):
    if not res:
        return None
    try:
        # get_current_user ya maneja la validación del token de forma centralizada
        return get_current_user(credentials=res, db=db)
    except Exception:
        return None

# ── GET /events/ ──────────────────────────────────────────────────────────────
# Sin auth        → solo aprobados + públicos
# Autenticado(4)  → solo aprobados (ambas visibilidades)
# Líder(3)        → todos los de su comunidad
# Admin(1)        → todos
@router.get("/", response_model=list[schemas.EventResponse])
def get_events(
    db: Session = Depends(get_db),
    current=Depends(get_optional_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    upcoming_only: bool = Query(True, description="Solo eventos futuros (event_date >= hoy)"),
    community_id: Optional[int] = Query(None, description="Filtrar por comunidad"),
    event_type: Optional[str] = Query(None, description="Filtrar por tipo: presencial | virtual"),
):
    if current is None:
        return service.list_approved_public(db, skip, limit, upcoming_only, community_id, event_type)
    # Si es Admin(1), respetamos el parámetro upcoming_only (por defecto False para admin si queremos ver todo)
    if current.rol_id == 1:
        # Para el admin, permitimos ver todo el historial si upcoming_only es False
        return service.list_all(db, skip, limit, upcoming_only, community_id, event_type)
    if current.rol_id == 3:
        return service.list_by_community(db, current.community_id, skip, limit, upcoming_only, event_type)
    return service.list_approved_for_user(db, current.community_id, skip, limit, upcoming_only, event_type, user_id=current.id)



# ── GET /events/pending ───────────────────────────────────────────────────────
# Líder: ve eventos pendientes de su comunidad; Admin: todos los pendientes
@router.get("/pending", response_model=list[schemas.EventResponse])
def get_pending_events(db: Session = Depends(get_db), current=Depends(get_current_user)):
    if current.rol_id not in [1, 3]:
        raise HTTPException(status_code=403, detail="Solo líder o admin")
    if current.rol_id == 1:
        return service.list_all_pending(db)
    return service.list_pending_by_community(db, current.community_id)

# ── GET próximos eventos ───────────────────────────────────────────────────────
@router.get("/upcoming", response_model=list[schemas.EventResponse])
def get_upcoming_events(db: Session = Depends(get_db), current=Depends(get_optional_user)):
    public_only = current is None
    return service.get_upcoming_events(db, limit=5, public_only=public_only)

# ── GET mis eventos (creados por el usuario actual) ────────────────────────────
@router.get("/my", response_model=list[schemas.EventResponse])
def get_my_events(
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    return service.list_by_creator(db, current.id, skip, limit)

# ── GET evento por ID ──────────────────────────────────────────────────────────
@router.get("/{event_id}", response_model=schemas.EventResponse)
def get_event(event_id: int, db: Session = Depends(get_db), current=Depends(get_optional_user)):
    event = repository.get_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    # Visitante: solo eventos aprobados y públicos
    if current is None:
        if event.status != "approved" or event.visibility != "publico":
            raise HTTPException(status_code=404, detail="Evento no encontrado")
    # Admin: ve todo
    elif current.rol_id == 1:
        pass
    # Líder: ve su comunidad
    elif current.rol_id == 3:
        if event.community_id != current.community_id and event.status != "approved":
            raise HTTPException(status_code=404, detail="Evento no encontrado")
    # Usuario autenticado: solo aprobados
    else:
        if event.status != "approved":
            raise HTTPException(status_code=404, detail="Evento no encontrado")

    comm = db.query(Community).filter(Community.id_community == event.community_id).first()
    if comm:
        event.community_name = comm.name_community
        leader = db.query(User).filter(User.id == comm.leader_id).first()
        event.leader_name = leader.name_user if leader else None
    else:
        event.community_name = None
        event.leader_name = None
    event.registered_count = repository.count_registrations(db, event_id)
    return event

# ── GET verificar si el usuario está registrado ────────────────────────────────
@router.get("/{event_id}/registration")
def check_registration(event_id: int, db: Session = Depends(get_db), current=Depends(get_current_user)):
    event = repository.get_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    registered = repository.get_registration(db, event_id, current.id) is not None
    return {"registered": registered, "event_id": event_id}

# ── POST subir imagen de evento ────────────────────────────────────────────────
@router.post("/upload-image")
async def upload_event_image(file: UploadFile = File(...), current=Depends(get_current_user)):
    if current.rol_id not in [1, 3]:
        raise HTTPException(status_code=403, detail="No tienes permisos para subir imágenes")

    ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
    MAX_SIZE_MB = 5
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Tipo de archivo no permitido. Usa JPG, PNG, WEBP o GIF")

    contents = await file.read()
    if len(contents) > MAX_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"La imagen no puede superar {MAX_SIZE_MB}MB")

    url = upload_image(io.BytesIO(contents), folder="events")
    if not url:
        raise HTTPException(status_code=500, detail="Error al subir la imagen a Cloudinary")
    return {"url": url}

# ── POST crear evento ──────────────────────────────────────────────────────────
# Admin(1), líder(3), pueden crear eventos
# Líder se auto-asigna a su comunidad
# Regla de negocio:
# - Eventos PRIVADOS → se aprueban automáticamente (admin o líder)
# - Eventos PÚBLICOS → si los crea un líder quedan pendientes; si los crea el admin se aprueban al crearse
@router.post("/", response_model=schemas.EventResponse)
def create_event(data: schemas.EventCreate, db: Session = Depends(get_db), current=Depends(get_current_user)):
    if current.rol_id not in [1, 3]:
        raise HTTPException(status_code=403, detail="No tienes permisos para crear eventos")

    if current.rol_id == 3:
        # El líder siempre crea eventos en su propia comunidad
        data = data.model_copy(update={"community_id": current.community_id})

    # Asignar creador
    data = data.model_copy(update={"creator_id": current.id})

    # Determinar si se auto-aprueba según visibilidad y rol
    visibility = data.visibility or "publico"
    auto_approve = False

    # Eventos privados: siempre auto-aprobados
    if visibility == "privado":
        auto_approve = True
    # Eventos públicos: solo el admin los puede auto-aprobar al crearlos
    elif visibility == "publico" and current.rol_id == 1:
        auto_approve = True

    event = service.create_event(db, data, auto_approve=auto_approve)
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
    # Solo el administrador puede aprobar eventos
    if current.rol_id != 1:
        raise HTTPException(status_code=403, detail="Solo el administrador puede aprobar eventos")

    event = repository.get_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    # Solo tiene sentido aprobar eventos públicos que estén pendientes
    if event.visibility != "publico" or event.status != "pending":
        raise HTTPException(status_code=400, detail="Solo se pueden aprobar eventos públicos en estado pendiente")

    return service.approve_event(db, event_id)

# ── PATCH rechazar evento ──────────────────────────────────────────────────────
@router.patch("/{event_id}/reject", response_model=schemas.EventResponse)
def reject_event(event_id: int, db: Session = Depends(get_db), current=Depends(get_current_user)):
    # Solo el administrador puede rechazar eventos
    if current.rol_id != 1:
        raise HTTPException(status_code=403, detail="Solo el administrador puede rechazar eventos")

    event = repository.get_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    # Solo tiene sentido rechazar eventos públicos que estén pendientes
    if event.visibility != "publico" or event.status != "pending":
        raise HTTPException(status_code=400, detail="Solo se pueden rechazar eventos públicos en estado pendiente")

    return service.reject_event(db, event_id)

# ── PATCH cancelar evento ──────────────────────────────────────────────────────
@router.patch("/{event_id}/cancel", response_model=schemas.EventResponse)
def cancel_event(event_id: int, db: Session = Depends(get_db), current=Depends(get_current_user)):
    if current.rol_id not in [1, 3]:
        raise HTTPException(status_code=403, detail="No tienes permisos para cancelar eventos")

    event = repository.get_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    if current.rol_id == 3 and event.community_id != current.community_id:
        raise HTTPException(status_code=403, detail="Solo puedes cancelar eventos de tu comunidad")

    return service.cancel_event(db, event_id)

# ── PATCH aplazar evento ───────────────────────────────────────────────────────
@router.patch("/{event_id}/postpone", response_model=schemas.EventResponse)
def postpone_event(event_id: int, db: Session = Depends(get_db), current=Depends(get_current_user)):
    if current.rol_id not in [1, 3]:
        raise HTTPException(status_code=403, detail="No tienes permisos para aplazar eventos")

    event = repository.get_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    if current.rol_id == 3 and event.community_id != current.community_id:
        raise HTTPException(status_code=403, detail="Solo puedes aplazar eventos de tu comunidad")

    return service.postpone_event(db, event_id)

# ── POST registrarse a un evento ──────────────────────────────────────────────
@router.post("/{event_id}/register")
def register_to_event(event_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current=Depends(get_current_user)):

    # Valida duplicado, capacidad y status — lanza HTTPException si falla
    service.register_user_to_event(db, event_id, current.id)

    event = repository.get_by_id(db, event_id)
    user = db.query(User).filter(User.id == current.id).first()
    community = db.query(Community).filter(Community.id_community == event.community_id).first()

    # Email de confirmación al usuario
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

    # Notificar al líder
    if community and community.leader_id:
        total = repository.count_registrations(db, event_id)
        add_notification(
            db,
            "Nueva Inscripción",
            f"{user.name_user} se registró en '{event.title}'. Total inscritos: {total}/{event.capacity or '∞'}",
            "event",
            recipient_id=community.leader_id
        )

    # Notificar al usuario
    add_notification(
        db,
        "¡Inscripción Exitosa!",
        f"Te registraste en '{event.title}'. Revisa tu correo para más detalles.",
        "info",
        recipient_id=current.id
    )

    return {"message": "Registro exitoso", "event_title": event.title}


# ── DELETE cancelar registro a un evento ───────────────────────────────────────
@router.delete("/{event_id}/register")
def unregister_from_event(event_id: int, db: Session = Depends(get_db), current=Depends(get_current_user)):
    service.unregister_user_from_event(db, event_id, current.id)
    return {"message": "Registro cancelado correctamente"}


# ── GET asistentes de un evento ────────────────────────────────────────────────
# Solo líder de la comunidad o admin
@router.get("/{event_id}/attendees")
def get_event_attendees(event_id: int, db: Session = Depends(get_db), current=Depends(get_current_user)):
    if current.rol_id not in [1, 3]:
        raise HTTPException(status_code=403, detail="Solo líder o admin puede ver los asistentes")
    result = service.get_event_attendees(db, event_id, current.rol_id, current.community_id)
    return {
        "total": result["total"],
        "capacity": result["capacity"],
        "attendees": [{"id": u.id, "name": u.name_user, "email": u.email} for u in result["attendees"]]
    }

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
