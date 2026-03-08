from sqlalchemy.orm import Session
from . import repository, schemas

def list_courses(db: Session):
    return repository.get_all(db)

def get_course(db: Session, course_id: int):
    return repository.get_by_id(db, course_id)

def create_course(db: Session, course: schemas.CourseCreate):
    return repository.create(db, course)

def update_course(db: Session, course_id: int, data: schemas.CourseUpdate):
    return repository.update(db, course_id, data.model_dump(exclude_unset=True))

def delete_course(db: Session, course_id: int):
    return repository.delete(db, course_id)
