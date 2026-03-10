from sqlalchemy.orm import Session
from . import repository, schemas


def list_technologies(db: Session):
    return repository.get_all_technologies(db)


def create_technology(db: Session, tech: schemas.TechnologyCreate):
    return repository.create_technology(db, tech)


def delete_technology(db: Session, tech_id: int):
    return repository.delete_technology(db, tech_id)
