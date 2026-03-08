from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.auth.router import get_current_user
from app.core.cloudinary_service import upload_image
from . import schemas, service

router = APIRouter(prefix="/communities", tags=["Communities"])

# Creación protegida
@router.post("/", response_model=schemas.CommunityResponse)
def create_community(data: schemas.CommunityCreate, db: Session = Depends(get_db), current=Depends(get_current_user)):
    return service.create_community(db, data)

# Subida de imagen a Cloudinary
@router.post("/upload")
async def upload_community_logo(file: UploadFile = File(...), current=Depends(get_current_user)):
    url = upload_image(file.file, folder="communities")
    if not url:
        raise HTTPException(status_code=500, detail="Error al subir la imagen a Cloudinary")
    return {"url": url}

# Listado filtrado por dueño
@router.get("/", response_model=list[schemas.CommunityResponse])
def get_communities(db: Session = Depends(get_db), current=Depends(get_current_user)):
    return service.list_communities(db, current_user=current)

# Actualización protegida
@router.patch("/{id}", response_model=schemas.CommunityResponse)
def update_community(id: int, data: schemas.CommunityUpdate, db: Session = Depends(get_db)): #, current=Depends(get_current_user)):
    return service.update_community(db, id, data)

# Eliminación protegida
@router.delete("/{id}")
def delete_community(id: int, db: Session = Depends(get_db)): #, current=Depends(get_current_user)):
    return service.delete_community(db, id)