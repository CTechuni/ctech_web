from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.auth.router import get_current_user # Candado
from . import schemas, service

router = APIRouter(prefix="/courses", tags=["Courses"])

# GET público (Sin candado en la imagen)
@router.get("/", response_model=list[schemas.CourseResponse])
def get_courses(db: Session = Depends(get_db)):
    return service.list_courses(db)

# Endpoints protegidos (Con candado en la imagen)
@router.post("/", response_model=schemas.CourseResponse)
def create_course(data: schemas.CourseCreate, db: Session = Depends(get_db), current=Depends(get_current_user)):
    return service.create_course(db, data)

@router.get("/{id}", response_model=schemas.CourseResponse)
def get_course(id: int, db: Session = Depends(get_db), current=Depends(get_current_user)):
    course = service.get_course(db, id)
    if not course:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    
    # Lógica de Privacidad: Estudiantes y Líderes solo ven cursos de su comunidad
    user_role = str(current.role).lower()
    if user_role in ['user', 'usuario', 'leader'] and course.community_id != current.community_id:
        raise HTTPException(status_code=403, detail="Acceso denegado: este curso pertenece a otra comunidad")
        
    return course

@router.put("/{id}", response_model=schemas.CourseResponse)
def update_course(id: int, data: schemas.CourseUpdate, db: Session = Depends(get_db), current=Depends(get_current_user)):
    return service.update_course(db, id, data)

@router.delete("/{id}")
def delete_course(id: int, db: Session = Depends(get_db), current=Depends(get_current_user)):
    return service.delete_course(db, id)

