from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from . import schemas, service

router = APIRouter(prefix="/technologies", tags=["Technologies"])

@router.get("/", response_model=list[schemas.TechnologyResponse])
def get_all(db: Session = Depends(get_db)):
    """Lista las tecnologías para los cursos de CTech."""
    return service.list_technologies(db)

@router.post("/", response_model=schemas.TechnologyResponse)
def create(data: schemas.TechnologyCreate, db: Session = Depends(get_db)):
    """
    IMPORTANTE: Verifique la ortografía antes de enviar. 
    Esta acción no permite edición ni eliminación posterior.
    """
    return service.add_technology(db, data)