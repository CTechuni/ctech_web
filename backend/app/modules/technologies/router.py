from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.auth.router import get_current_user
from . import schemas, service

router = APIRouter(prefix="/technologies", tags=["Technologies"])

@router.get("/", response_model=list[schemas.TechnologyResponse])
def get_all(db: Session = Depends(get_db)):
    """Lista las tecnologías para los cursos de CTech."""
    return service.list_technologies(db)

@router.post("/", response_model=schemas.TechnologyResponse)
def create(data: schemas.TechnologyCreate, db: Session = Depends(get_db), current=Depends(get_current_user)):
    """Admin y líder pueden agregar tecnologías al catálogo."""
    if current.rol_id not in [1, 3]:
        raise HTTPException(status_code=403, detail="Solo el administrador o un líder puede crear tecnologías")
    return service.add_technology(db, data)