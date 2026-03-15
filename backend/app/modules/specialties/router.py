from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.auth.router import get_current_user
from . import schemas, repository

router = APIRouter(prefix="/specialties", tags=["Specialties"])

@router.get("/", response_model=list[schemas.SpecialtyResponse])
def list_specialties(db: Session = Depends(get_db)):
    return repository.get_all(db)

@router.post("/", response_model=schemas.SpecialtyResponse)
def create_specialty(
    data: schemas.SpecialtyCreate, 
    db: Session = Depends(get_db), 
    current=Depends(get_current_user)
):
    # Solo Admin (1) o Líder (3) pueden crear categorías
    if current.rol_id not in [1, 3]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="No tienes permisos para crear categorías"
        )
    return repository.create(db, data)
