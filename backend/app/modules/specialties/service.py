from sqlalchemy.orm import Session
from . import repository

def list_specialties(db: Session):
    return repository.get_all(db)

def add_specialty(db: Session, specialty_data):
    # Aquí podrías validar que el nombre no esté vacío antes de guardar
    return repository.create(db, specialty_data.name)