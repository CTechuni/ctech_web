from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from . import schemas, service

router = APIRouter(prefix="/specialties", tags=["Specialties"])

@router.get("/", response_model=list[schemas.SpecialtyResponse])
def get_specialties(db: Session = Depends(get_db)):
    """Lista todas las especialidades disponibles para los perfiles de CTech."""
    return service.list_specialties(db)

@router.post("/", response_model=schemas.SpecialtyResponse)
def create_specialty(data: schemas.SpecialtyCreate, db: Session = Depends(get_db)):
    """Agrega una nueva especialidad al catálogo maestro."""
    return service.add_specialty(db, data)
    