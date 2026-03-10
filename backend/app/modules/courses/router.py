from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.auth.router import get_current_user
from . import schemas, service

router = APIRouter(prefix="/courses", tags=["Courses"])

# GET público — solo cursos aprobados
@router.get("/", response_model=list[schemas.CourseResponse])
def get_courses(db: Session = Depends(get_db)):
    return service.list_approved_courses(db)

# GET cursos pendientes — solo líder (su comunidad) o admin
@router.get("/pending", response_model=list[schemas.CourseResponse])
def get_pending_courses(db: Session = Depends(get_db), current=Depends(get_current_user)):
    if current.rol_id not in [1, 3]:
        raise HTTPException(status_code=403, detail="Solo líderes y administradores pueden ver cursos pendientes")
    community_id = None if current.rol_id == 1 else current.community_id
    return service.list_pending_courses(db, community_id)

# GET todos los cursos — solo admin
@router.get("/all", response_model=list[schemas.CourseResponse])
def get_all_courses(db: Session = Depends(get_db), current=Depends(get_current_user)):
    if current.rol_id != 1:
        raise HTTPException(status_code=403, detail="Solo el administrador puede ver todos los cursos")
    return service.list_all_courses(db)

# GET mis cursos — mentor autenticado
@router.get("/my", response_model=list[schemas.CourseResponse])
def get_my_courses(db: Session = Depends(get_db), current=Depends(get_current_user)):
    if current.rol_id != 2:
        raise HTTPException(status_code=403, detail="Solo los mentores pueden ver sus cursos")
    return repository.get_by_mentor(db, current.id)

# GET detalle de curso
@router.get("/{id}", response_model=schemas.CourseResponse)
def get_course(id: int, db: Session = Depends(get_db)):
    course = service.get_course(db, id)
    if not course:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    return course

# POST — solo mentor, se auto-asigna como mentor_id y el curso queda en "pending"
@router.post("/", response_model=schemas.CourseResponse)
def create_course(data: schemas.CourseCreate, db: Session = Depends(get_db), current=Depends(get_current_user)):
    if current.rol_id != 2:
        raise HTTPException(status_code=403, detail="Solo los mentores pueden crear cursos")
    data = data.model_copy(update={
        "mentor_id": current.id,
        "community_id": current.community_id
    })
    return service.create_course(db, data)

# PATCH aprobar — solo líder de la misma comunidad o admin
@router.patch("/{id}/approve", response_model=schemas.CourseResponse)
def approve_course(id: int, db: Session = Depends(get_db), current=Depends(get_current_user)):
    if current.rol_id not in [1, 3]:
        raise HTTPException(status_code=403, detail="Solo líderes y administradores pueden aprobar cursos")
    course = service.get_course(db, id)
    if not course:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    if current.rol_id == 3 and course.community_id != current.community_id:
        raise HTTPException(status_code=403, detail="Solo puedes aprobar cursos de tu propia comunidad")
    return service.update_course_status(db, id, "approved")

# PATCH rechazar — solo líder de la misma comunidad o admin
@router.patch("/{id}/reject", response_model=schemas.CourseResponse)
def reject_course(id: int, db: Session = Depends(get_db), current=Depends(get_current_user)):
    if current.rol_id not in [1, 3]:
        raise HTTPException(status_code=403, detail="Solo líderes y administradores pueden rechazar cursos")
    course = service.get_course(db, id)
    if not course:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    if current.rol_id == 3 and course.community_id != current.community_id:
        raise HTTPException(status_code=403, detail="Solo puedes rechazar cursos de tu propia comunidad")
    return service.update_course_status(db, id, "rejected")

# PUT editar — solo el mentor dueño del curso
@router.put("/{id}", response_model=schemas.CourseResponse)
def update_course(id: int, data: schemas.CourseUpdate, db: Session = Depends(get_db), current=Depends(get_current_user)):
    if current.rol_id != 2:
        raise HTTPException(status_code=403, detail="Solo el mentor puede editar su curso")
    course = service.get_course(db, id)
    if not course:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    if course.mentor_id != current.id:
        raise HTTPException(status_code=403, detail="Solo puedes editar tus propios cursos")
    # Si pasa de borrador a pendiente, notificar al líder
    was_draft = course.status == "draft"
    updated = service.update_course(db, id, data)
    if was_draft and updated.status == "pending":
        from app.modules.notifications import service as notification_service
        from app.modules.communities.models import Community
        comm = db.query(Community).filter(Community.id_community == updated.community_id).first()
        community_name = comm.name_community if comm else "Sin Comunidad"
        notification_service.add_notification(
            db,
            "Curso pendiente de aprobación",
            f"El mentor {current.name_user} ha enviado el curso '{updated.title}' en {community_name} para revisión.",
            "course"
        )
    return updated

# DELETE — solo el mentor dueño o admin
@router.delete("/{id}")
def delete_course(id: int, db: Session = Depends(get_db), current=Depends(get_current_user)):
    if current.rol_id not in [1, 2]:
        raise HTTPException(status_code=403, detail="No tienes permisos para eliminar este curso")
    course = service.get_course(db, id)
    if not course:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    if current.rol_id == 2 and course.mentor_id != current.id:
        raise HTTPException(status_code=403, detail="Solo puedes eliminar tus propios cursos")
    return service.delete_course(db, id)

