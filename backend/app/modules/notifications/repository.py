from sqlalchemy.orm import Session
from . import models

def create(db: Session, data: dict):
    notification = models.Notification(**data)
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification

def get_all(db: Session, limit: int = 20):
    return db.query(models.Notification).order_by(models.Notification.created_at.desc()).limit(limit).all()

def mark_as_read(db: Session, notification_id: int):
    notification = db.query(models.Notification).filter(models.Notification.id == notification_id).first()
    if notification:
        notification.is_read = True
        db.commit()
        db.refresh(notification)
    return notification

def mark_all_as_read(db: Session):
    db.query(models.Notification).filter(models.Notification.is_read == False).update({"is_read": True})
    db.commit()
