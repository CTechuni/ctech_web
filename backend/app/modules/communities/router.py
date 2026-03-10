from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.auth.router import get_current_user
from app.core.cloudinary_service import upload_image
from . import schemas, service

router = APIRouter(prefix="/communities", tags=["Communities"])

# Creación protegida — solo admin
@router.post("/", response_model=schemas.CommunityResponse)
def create_community(data: schemas.CommunityCreate, db: Session = Depends(get_db), current=Depends(get_current_user)):
    if current.rol_id != 1:
        raise HTTPException(status_code=403, detail="Solo el administrador puede crear comunidades")
    return service.create_community(db, data)

# Subida de imagen a Cloudinary
@router.post("/upload")
async def upload_community_logo(file: UploadFile = File(...), current=Depends(get_current_user)):
    url = upload_image(file.file, folder="communities")
    if not url:
        raise HTTPException(status_code=500, detail="Error al subir la imagen a Cloudinary")
    return {"url": url}

# Listado público para registro
@router.get("/public", response_model=list[schemas.CommunityPublicResponse])
def get_public_communities(db: Session = Depends(get_db)):
    return service.list_communities(db)

# Listado de comunidades con logo para la landing
@router.get("/with-logo", response_model=list[schemas.CommunityPublicResponse])
def get_communities_with_logo(db: Session = Depends(get_db)):
    return service.list_with_logo(db)

# Listado filtrado por dueño
@router.get("/", response_model=list[schemas.CommunityResponse])
def get_communities(db: Session = Depends(get_db), current=Depends(get_current_user)):
    return service.list_communities(db, current_user=current)

# Actualización protegida (solo admin)
@router.patch("/{id}", response_model=schemas.CommunityResponse)
def update_community(id: int, data: schemas.CommunityUpdate, db: Session = Depends(get_db), current=Depends(get_current_user)):
    if current.rol_id != 1:
        raise HTTPException(status_code=403, detail="Solo el administrador puede editar comunidades")
    return service.update_community(db, id, data)

# Eliminación protegida (solo admin)
@router.delete("/{id}")
def delete_community(id: int, db: Session = Depends(get_db), current=Depends(get_current_user)):
    if current.rol_id != 1:
        raise HTTPException(status_code=403, detail="Solo el administrador puede eliminar comunidades")
    return service.delete_community(db, id)