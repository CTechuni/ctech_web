from sqlalchemy.orm import Session
from fastapi import HTTPException
from . import repository

def book_session(db: Session, session_id: int, student_id: int):
    session = repository.update_status(db, session_id, student_id, "reserved")
    if not session:
        raise HTTPException(status_code=400, detail="No se pudo realizar la reserva.")
    return session

def cancel_session(db: Session, session_id: int):
    # Regresa la sesión al estado disponible
    return repository.update_status(db, session_id, None, "available")
