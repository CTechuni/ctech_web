from sqlalchemy.orm import Session
from . import repository, schemas, models
from app.modules.notifications import service as notification_service
from app.modules.communities.models import Community
from app.modules.users.models import User

def list_approved_courses(db: Session):
    return repository.get_by_status(db, "approved")

def list_pending_courses(db: Session, community_id: int = None):
    return repository.get_by_status(db, "pending", community_id)

def list_all_courses(db: Session):
    return repository.get_all(db)

def get_course(db: Session, course_id: int):
    return repository.get_by_id(db, course_id)

def create_course(db: Session, course: schemas.CourseCreate):
    # Normalizar estado: solo "draft" o "pending"
    if course.status not in ("draft", "pending"):
        course = course.model_copy(update={"status": "pending"})
    new_course = repository.create(db, course)
    # Solo notificar al líder si el curso se envía a revisión
    if new_course and new_course.status == "pending":
        community_name = "Sin Comunidad"
        mentor_name = "Mentor Desconocido"
        comm = db.query(Community).filter(Community.id_community == new_course.community_id).first()
        if comm: community_name = comm.name_community
        mentor = db.query(User).filter(User.id == new_course.mentor_id).first()
        if mentor: mentor_name = mentor.name_user
        notification_service.add_notification(
            db,
            "Curso pendiente de aprobación",
            f"El mentor {mentor_name} ha creado el curso '{new_course.title}' en {community_name}. Revisalo para aprobarlo o rechazarlo.",
            "course"
        )
    return new_course

def update_course(db: Session, course_id: int, data: schemas.CourseUpdate):
    return repository.update(db, course_id, data.model_dump(exclude_unset=True))

def update_course_status(db: Session, course_id: int, status: str):
    return repository.update(db, course_id, {"status": status})

def delete_course(db: Session, course_id: int):
    return repository.delete(db, course_id)
