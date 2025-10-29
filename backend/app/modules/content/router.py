from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.modules.content import schemas, service

router = APIRouter(prefix="/contenido", tags=["Contenido Educativo"])

@router.get("/", response_model=List[schemas.EducationalContentResponse])
def listar_contenidos(db: Session = Depends(get_db)):
    return service.list_contents(db)

@router.get("/{content_id}", response_model=schemas.EducationalContentResponse)
def obtener_contenido(content_id: int, db: Session = Depends(get_db)):
    content = service.get_content(db, content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Contenido no encontrado")
    return content

@router.post("/", response_model=schemas.EducationalContentResponse)
def crear_contenido(
    contenido: schemas.EducationalContentCreate = Body(...),
    db: Session = Depends(get_db)
):
    return service.create_content(db, contenido)

@router.put("/{content_id}", response_model=schemas.EducationalContentResponse)
def actualizar_contenido(
    content_id: int,
    contenido: schemas.EducationalContentUpdate = Body(...),
    db: Session = Depends(get_db)
):
    content = service.update_content(db, content_id, contenido)
    if not content:
        raise HTTPException(status_code=404, detail="Contenido no encontrado")
    return content

@router.delete("/{content_id}")
def eliminar_contenido(content_id: int, db: Session = Depends(get_db)):
    eliminado = service.delete_content(db, content_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Contenido no encontrado")
    return {"message": "Contenido eliminado correctamente"}