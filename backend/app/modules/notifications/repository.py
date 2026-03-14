from sqlalchemy.orm import Session
from . import models

def create(db: Session, data: dict):
    notification = models.Notification(**data)
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification

def get_all(db: Session, user_id: int = None, is_admin: bool = False, limit: int = 20):
    query = db.query(models.Notification)
    
    if not is_admin:
        # Los usuarios normales (líderes) solo ven lo dirigido a ellos
        query = query.filter(models.Notification.recipient_id == user_id)
    else:
        # Los admins ven todo o lo que no tiene destinatario específico (según preferencia)
        # Vamos a dejar que el admin vea todo por ahora
        pass
        
    return query.order_by(models.Notification.created_at.desc()).limit(limit).all()

def mark_as_read(db: Session, notification_id: int, user_id: int):
    notification = db.query(models.Notification).filter(
        models.Notification.id == notification_id,
        models.Notification.recipient_id == user_id
    ).first()
    if notification:
        notification.is_read = True
        db.commit()
        db.refresh(notification)
    return notification

def mark_all_as_read(db: Session, user_id: int):
    db.query(models.Notification).filter(
        models.Notification.recipient_id == user_id,
        models.Notification.is_read == False
    ).update({"is_read": True})
    db.commit()
