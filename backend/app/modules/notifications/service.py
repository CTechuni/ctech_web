from sqlalchemy.orm import Session
from . import repository

def add_notification(db: Session, title: str, message: str, type: str):
    """
    Agrega una notificación global para los administradores.
    """
    data = {
        "title": title,
        "message": message,
        "type": type
    }
    return repository.create(db, data)

def list_notifications(db: Session, limit: int = 20):
    return repository.get_all(db, limit)

def mark_as_read(db: Session, notification_id: int):
    return repository.mark_as_read(db, notification_id)

def mark_all_as_read(db: Session):
    return repository.mark_all_as_read(db)
