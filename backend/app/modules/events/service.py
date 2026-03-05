from sqlalchemy.orm import Session
from . import repository

def list_events(db: Session):
    return repository.get_all(db)

def create_event(db: Session, data):
    return repository.create(db, data)

def process_image_upload(db: Session, event_id: int, file_url: str):
    # Aquí iría la lógica de validación de formato antes de guardar
    return repository.update_image(db, event_id, file_url)
