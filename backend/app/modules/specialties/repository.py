from sqlalchemy.orm import Session
from . import models, schemas

def get_all(db: Session):
    return db.query(models.Specialty).all()

def create(db: Session, data: schemas.SpecialtyCreate):
    db_item = models.Specialty(name=data.name)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
