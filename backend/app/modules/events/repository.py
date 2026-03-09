from sqlalchemy.orm import Session
from . import models, schemas
from app.modules.communities.models import Community

def get_all(db: Session):
    return db.query(
        models.Event,
        Community.name_community.label("community_name")
    ).outerjoin(
        Community, models.Event.community_id == Community.id_community
    ).order_by(models.Event.event_date.asc()).all()


def create(db: Session, event_data: schemas.EventCreate):
    db_event = models.Event(**event_data.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def get_upcoming(db: Session, limit: int = 5):
    from datetime import date
    today = date.today()
    return db.query(
        models.Event,
        Community.name_community.label("community_name")
    ).outerjoin(
        Community, models.Event.community_id == Community.id_community
    ).filter(
        models.Event.event_date >= today
    ).order_by(
        models.Event.event_date.asc(), 
        models.Event.event_time.asc()
    ).limit(limit).all()

def update_image(db: Session, event_id: int, url: str):
    db_event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if db_event:
        db_event.image_url = url
        db.commit()
    return db_event
