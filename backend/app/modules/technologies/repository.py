from sqlalchemy.orm import Session
from . import models

def get_all(db: Session):
    return db.query(models.Technology).order_by(models.Technology.name.asc()).all()

def get_by_name(db: Session, name: str):
    return db.query(models.Technology).filter(models.Technology.name.ilike(name)).first()

def create(db: Session, name: str):
    db_tech = models.Technology(name=name)
    db.add(db_tech)
    db.commit()
    db.refresh(db_tech)
    return db_tech