from sqlalchemy.orm import Session
from . import models

def get_by_course(db: Session, course_id: int):
    return db.query(models.MentoringSession).filter(
        models.MentoringSession.course_id == course_id,
        models.MentoringSession.status == "available"
    ).all()

def create(db: Session, session_dict: dict):
    db_session = models.MentoringSession(**session_dict)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def update_status(db: Session, session_id: int, student_id: Optional[int], status: str):
    db_session = db.query(models.MentoringSession).filter(models.MentoringSession.id == session_id).first()
    if db_session:
        db_session.student_id = student_id
        db_session.status = status
        db.commit()
        db.refresh(db_session)
    return db_session
