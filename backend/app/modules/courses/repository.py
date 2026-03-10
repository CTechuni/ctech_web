from sqlalchemy.orm import Session
from . import models, schemas

def get_all(db: Session):
    return db.query(models.Course).all()

def get_by_mentor(db: Session, mentor_id: int):
    return db.query(models.Course).filter(models.Course.mentor_id == mentor_id).all()

def get_by_status(db: Session, status: str, community_id: int = None):
    query = db.query(models.Course).filter(models.Course.status == status)
    if community_id is not None:
        query = query.filter(models.Course.community_id == community_id)
    return query.all()

def get_by_id(db: Session, course_id: int):
    return db.query(models.Course).filter(models.Course.id == course_id).first()

def create(db: Session, course: schemas.CourseCreate):
    db_course = models.Course(**course.model_dump())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

def update(db: Session, course_id: int, data: dict):
    db.query(models.Course).filter(models.Course.id == course_id).update(data)
    db.commit()
    return get_by_id(db, course_id)

def delete(db: Session, course_id: int):
    course = get_by_id(db, course_id)
    if course:
        db.delete(course)
        db.commit()
    return course
