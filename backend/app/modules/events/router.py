from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.auth.router import get_current_user
from . import schemas, service

router = APIRouter(prefix="/events", tags=["Events"])

@router.get("/", response_model=list[schemas.EventResponse])
def get_events(db: Session = Depends(get_db)):
    return service.list_events(db)

@router.post("/", response_model=schemas.EventResponse)
def create_event(data: schemas.EventCreate, db: Session = Depends(get_db), current=Depends(get_current_user)):
    return service.create_event(db, data)

@router.post("/upload") # Endpoint para la imagen según el Swagger
def upload_event_image(file: UploadFile = File(...), current=Depends(get_current_user)):
    # Simulación de subida a Cloudinary
    return {"url": "https://cloudinary.com/v1/image.png"}
