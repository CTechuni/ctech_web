from sqlalchemy.orm import Session
from . import repository
from app.modules.notifications import service as notification_service
from app.modules.communities.models import Community

def _attach_names(results):
    events = []
    for event, community_name, registered_count in results:
        event.community_name = community_name
        event.registered_count = registered_count
        events.append(event)
    return events

def list_approved_public(db: Session, skip: int = 0, limit: int = 20,
                         upcoming_only: bool = True, community_id: int | None = None,
                         event_type: str | None = None):
    return _attach_names(repository.get_approved_public(db, skip, limit, upcoming_only, community_id, event_type))

def list_approved(db: Session, skip: int = 0, limit: int = 20,
                  upcoming_only: bool = True, community_id: int | None = None,
                  event_type: str | None = None):
    return _attach_names(repository.get_approved(db, skip, limit, upcoming_only, community_id, event_type))

def list_all(db: Session, skip: int = 0, limit: int = 20,
             upcoming_only: bool = False, community_id: int | None = None,
             event_type: str | None = None):
    return _attach_names(repository.get_all(db, skip, limit, upcoming_only, community_id, event_type))

def list_by_community(db: Session, community_id: int, skip: int = 0, limit: int = 20,
                      upcoming_only: bool = False, event_type: str | None = None):
    return _attach_names(repository.get_by_community(db, community_id, skip, limit, upcoming_only, event_type))

def list_pending_by_community(db: Session, community_id: int):
    return _attach_names(repository.get_pending_by_community(db, community_id))

def list_all_pending(db: Session):
    return _attach_names(repository.get_all_pending(db))

def list_by_creator(db: Session, creator_id: int, skip: int = 0, limit: int = 20):
    return _attach_names(repository.get_by_creator(db, creator_id, skip, limit))

def create_event(db: Session, data, auto_approve: bool = False):
    if data.status not in ("draft", "pending"):
        data = data.model_copy(update={"status": "pending"})
    if auto_approve:
        data = data.model_copy(update={"status": "approved"})

    new_event = repository.create(db, data)

    if new_event and new_event.status == "pending":
        community_name = "Todas"
        if new_event.community_id:
            comm = db.query(Community).filter(Community.id_community == new_event.community_id).first()
            if comm:
                community_name = comm.name_community
        notification_service.add_notification(
            db,
            "Evento pendiente de aprobación",
            f"'{new_event.title}' fue enviado a revisión. Comunidad: {community_name}.",
            "event"
        )
    
    if new_event and new_event.status == "approved":
        notify_event_published(db, new_event)

    return new_event

def approve_event(db: Session, event_id: int):
    event = repository.approve(db, event_id)
    if event:
        # Notificar al creador del evento
        if event.creator_id:
            notification_service.add_notification(
                db,
                "Evento aprobado ✅",
                f"Tu evento '{event.title}' fue aprobado y ya es visible para la comunidad.",
                "event",
                recipient_id=event.creator_id
            )
        notify_event_published(db, event)
    return event

def reject_event(db: Session, event_id: int):
    event = repository.reject(db, event_id)
    if event:
        # Notificar al creador del evento
        if event.creator_id:
            notification_service.add_notification(
                db,
                "Evento rechazado ❌",
                f"Tu evento '{event.title}' fue rechazado por el líder de la comunidad.",
                "event",
                recipient_id=event.creator_id
            )
    return event

def notify_event_published(db: Session, event):
    """
    Notifica a usuarios sobre un nuevo evento publicado.
    - Privado: solo miembros de la comunidad (rol_id=4)
    - Público: todos los usuarios regulares (rol_id=4) del sistema
    En ambos casos excluye admins (1) y líderes (3).
    """
    from app.modules.users.models import User
    from app.modules.communities.models import Community

    query = db.query(User.id).filter(User.rol_id == 4)

    if event.visibility == "privado" and event.community_id:
        query = query.filter(User.community_id == event.community_id)

    user_ids = [r[0] for r in query.all()]

    comm = db.query(Community).filter(Community.id_community == event.community_id).first()
    comm_name = comm.name_community if comm else "CTech"

    for uid in user_ids:
        notification_service.add_notification(
            db,
            "Nuevo Evento Publicado 📢",
            f"Se ha publicado un nuevo evento: '{event.title}' en la comunidad {comm_name}.",
            "event",
            recipient_id=uid
        )

def get_upcoming_events(db: Session, limit: int = 5, public_only: bool = False):
    return _attach_names(repository.get_upcoming(db, limit, public_only))

def delete_event(db: Session, event_id: int):
    return repository.delete(db, event_id)

# ── Registro de asistentes ─────────────────────────────────────────────────────

def register_user_to_event(db: Session, event_id: int, user_id: int):
    from fastapi import HTTPException

    event = repository.get_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    if event.status != "approved":
        raise HTTPException(status_code=400, detail="Solo puedes registrarte a eventos aprobados")

    if repository.get_registration(db, event_id, user_id):
        raise HTTPException(status_code=409, detail="Ya estás registrado en este evento")

    if event.capacity is not None:
        count = repository.count_registrations(db, event_id)
        if count >= event.capacity:
            raise HTTPException(status_code=400, detail="El evento ya no tiene cupos disponibles")

    return repository.create_registration(db, event_id, user_id)

def unregister_user_from_event(db: Session, event_id: int, user_id: int):
    from fastapi import HTTPException

    if not repository.get_registration(db, event_id, user_id):
        raise HTTPException(status_code=404, detail="No estás registrado en este evento")

    return repository.delete_registration(db, event_id, user_id)

def get_event_attendees(db: Session, event_id: int, requester_rol_id: int, requester_community_id: int):
    from fastapi import HTTPException

    event = repository.get_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    if requester_rol_id == 3 and event.community_id != requester_community_id:
        raise HTTPException(status_code=403, detail="No tienes acceso a este evento")

    attendees = repository.get_registrations_by_event(db, event_id)
    count = repository.count_registrations(db, event_id)
    return {"total": count, "capacity": event.capacity, "attendees": attendees}
