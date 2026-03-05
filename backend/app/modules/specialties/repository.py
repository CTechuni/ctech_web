from sqlalchemy.orm import Session
from . import models

def get_all(db: Session):
    """Obtiene todas las especialidades ordenadas alfabéticamente."""
    return db.query(models.Specialty).order_by(models.Specialty.name.asc()).all()

def create(db: Session, name: str):
    """Registra una nueva especialidad en la base de datos."""
    db_specialty = models.Specialty(name=name)
    db.add(db_specialty)
    db.commit()
    db.refresh(db_specialty)
    return db_specialty