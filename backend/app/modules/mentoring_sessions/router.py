from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.auth.router import get_current_user
from . import schemas, service, repository

router = APIRouter(prefix="/sessions", tags=["Mentoring Sessions"])

@router.post("/", response_model=schemas.SessionResponse)
def create(data: schemas.SessionCreate, db: Session = Depends(get_db), current=Depends(get_current_user)):
    session_data = data.model_dump()
    session_data["mentor_id"] = current["user_id"]
    return repository.create(db, session_data)

@router.get("/course/{course_id}", response_model=list[schemas.SessionResponse])
def get_by_course(course_id: int, db: Session = Depends(get_db)):
    return repository.get_by_course(db, course_id)

@router.post("/{id}/reserve", response_model=schemas.SessionResponse)
def reserve(id: int, db: Session = Depends(get_db), current=Depends(get_current_user)):
    return service.book_session(db, id, current["user_id"])

@router.delete("/{id}/cancel")
def cancel(id: int, db: Session = Depends(get_db), current=Depends(get_current_user)):
    return service.cancel_session(db, id)
