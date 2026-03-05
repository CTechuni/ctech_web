from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from . import schemas, service

# Definimos el router que main.py está buscando
router = APIRouter()

@router.post("/register", response_model=schemas.UserOut, tags=["Users"])
def register_user(user: schemas.UserBase, db: Session = Depends(get_db)):
    return {"message": "Endpoint de registro listo"}

@router.get("/", tags=["Users"])
def list_users(db: Session = Depends(get_db)):
    return []

@router.get("/me", tags=["Users"])
def get_me():
    return {"user": "profile"}

@router.get("/leaders", tags=["Users"])
def list_leaders():
    return []