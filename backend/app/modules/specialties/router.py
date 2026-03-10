from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.auth.router import get_current_user
from . import schemas, service

router = APIRouter(prefix="/specialties", tags=["Specialties"])

@router.get("/", response_model=list[schemas.SpecialtyResponse])
def get_specialties(db: Session = Depends(get_db)):
    """Lista todas las especialidades disponibles para los perfiles de CTech."""
    return service.list_specialties(db)

@router.post("/", response_model=schemas.SpecialtyResponse)
def create_specialty(data: schemas.SpecialtyCreate, db: Session = Depends(get_db), current=Depends(get_current_user)):
    """Administrador y líder pueden agregar categorías/especialidades al catálogo."""
    if current.rol_id not in [1, 3]:
        raise HTTPException(status_code=403, detail="Solo el administrador o el líder pueden crear categorías")
    return service.add_specialty(db, data)
    