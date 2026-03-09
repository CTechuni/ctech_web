from sqlalchemy.orm import Session
from . import repository, schemas, models
from app.modules.notifications import service as notification_service
from app.modules.communities.models import Community
from app.modules.users.models import User

def list_courses(db: Session):
    return repository.get_all(db)

def get_course(db: Session, course_id: int):
    return repository.get_by_id(db, course_id)

def create_course(db: Session, course: schemas.CourseCreate):
    new_course = repository.create(db, course)
    if new_course:
        # Obtener nombres para la notificación
        community_name = "Sin Comunidad"
        mentor_name = "Mentor Desconocido"
        
        comm = db.query(Community).filter(Community.id_community == new_course.community_id).first()
        if comm: community_name = comm.name_community
        
        mentor = db.query(User).filter(User.id == new_course.mentor_id).first()
        if mentor: mentor_name = mentor.name_user
        
        notification_service.add_notification(
            db,
            "Nuevo Curso Creado ✨",
            f"Se ha publicado el curso '{new_course.title}' en la comunidad {community_name}. Mentor: {mentor_name}.",
            "course"
        )
    return new_course

def update_course(db: Session, course_id: int, data: schemas.CourseUpdate):
    return repository.update(db, course_id, data.model_dump(exclude_unset=True))

def delete_course(db: Session, course_id: int):
    return repository.delete(db, course_id)
