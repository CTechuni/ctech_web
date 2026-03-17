from sqlalchemy.orm import Session
from . import repository

def add_notification(db: Session, title: str, message: str, type: str, recipient_id: int = None):
    """
    Agrega una notificación. Si tiene recipient_id, es para un líder específico.
    Si no, es global (para administradores).
    """
    data = {
        "title": title,
        "message": message,
        "type": type,
        "recipient_id": recipient_id
    }
    return repository.create(db, data)

def list_notifications(db: Session, user_id: int = None, is_admin: bool = False, limit: int = 20):
    return repository.get_all(db, user_id=user_id, is_admin=is_admin, limit=limit)

def mark_as_read(db: Session, notification_id: int, user_id: int, is_admin: bool = False):
    return repository.mark_as_read(db, notification_id, user_id, is_admin=is_admin)

def mark_all_as_read(db: Session, user_id: int, is_admin: bool = False):
    return repository.mark_all_as_read(db, user_id, is_admin=is_admin)
