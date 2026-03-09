from sqlalchemy.orm import Session
from . import repository
from app.modules.notifications import service as notification_service
from app.modules.communities.models import Community

def list_events(db: Session):
    return repository.get_all(db)

def create_event(db: Session, data):
    new_event = repository.create(db, data)
    if new_event:
        # Título descriptivo según tipo
        is_private = new_event.event_type == "private"
        label = "Privado 🔒" if is_private else "Público 🌐"
        
        community_name = "Todas"
        if new_event.community_id:
            comm = db.query(Community).filter(Community.id_community == new_event.community_id).first()
            if comm: community_name = comm.name_community
            
        notification_service.add_notification(
            db,
            f"Nuevo Evento {label}",
            f"Se ha programado el evento '{new_event.title}' para el {new_event.event_date}. Comunidad: {community_name}.",
            "event"
        )
    return new_event

def process_image_upload(db: Session, event_id: int, file_url: str):
    # Aquí iría la lógica de validación de formato antes de guardar
    return repository.update_image(db, event_id, file_url)
