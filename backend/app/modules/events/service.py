from sqlalchemy.orm import Session
from . import repository
from app.modules.notifications import service as notification_service
from app.modules.communities.models import Community

def _attach_names(results):
    events = []
    for event, community_name in results:
        event.community_name = community_name
        events.append(event)
    return events

def list_approved_public(db: Session):
    return _attach_names(repository.get_approved_public(db))

def list_approved(db: Session):
    return _attach_names(repository.get_approved(db))

def list_all(db: Session):
    return _attach_names(repository.get_all(db))

def list_by_community(db: Session, community_id: int):
    return _attach_names(repository.get_by_community(db, community_id))

def list_pending_by_community(db: Session, community_id: int):
    return _attach_names(repository.get_pending_by_community(db, community_id))

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
    return new_event

def approve_event(db: Session, event_id: int):
    event = repository.approve(db, event_id)
    if event:
        notification_service.add_notification(
            db,
            "Evento aprobado ✅",
            f"El evento '{event.title}' fue aprobado y ya es visible para la comunidad.",
            "event"
        )
    return event

def reject_event(db: Session, event_id: int):
    event = repository.reject(db, event_id)
    if event:
        notification_service.add_notification(
            db,
            "Evento rechazado ❌",
            f"El evento '{event.title}' fue rechazado por el líder de la comunidad.",
            "event"
        )
    return event

def get_upcoming_events(db: Session, limit: int = 5, public_only: bool = False):
    return _attach_names(repository.get_upcoming(db, limit, public_only))

def delete_event(db: Session, event_id: int):
    return repository.delete(db, event_id)
