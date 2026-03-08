from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.auth.router import get_current_user
from . import schemas, service

router = APIRouter(prefix="/users", tags=["Users"])

# Público
# Protegido
@router.get("/", response_model=schemas.UserPaginationResponse)
def list_users(page: int = 1, limit: int = 6, db: Session = Depends(get_db), current=Depends(get_current_user)):
    return service.get_paginated(db, page, limit)

@router.get("/me", response_model=schemas.UserResponse)
def get_me(current=Depends(get_current_user), db: Session = Depends(get_db)):
    return service.get_user(db, current["user_id"])

@router.patch("/{user_id}/promote")
def promote(user_id: int, db: Session = Depends(get_db), current=Depends(get_current_user)):
    return service.change_role(db, user_id, 2) # 2 para Mentor

@router.patch("/{user_id}/demote")
def demote(user_id: int, db: Session = Depends(get_db), current=Depends(get_current_user)):
    return service.change_role(db, user_id, 4) # 4 para User estándar

@router.get("/leaders", response_model=list[schemas.UserResponse])
def get_leaders(db: Session = Depends(get_db)): #, current=Depends(get_current_user)):
    return service.list_leaders(db)

@router.get("/mentors", response_model=list[schemas.UserResponse])
def get_mentors(db: Session = Depends(get_db), current=Depends(get_current_user)):
    return service.list_mentors(db)

@router.patch("/{user_id}", response_model=schemas.UserResponse)
def update_user(user_id: int, data: schemas.UserUpdate, db: Session = Depends(get_db), current=Depends(get_current_user)):
    # exclude_unset=True ensures only the fields sent in the request are included
    return service.update_user(db, user_id, data.model_dump(exclude_unset=True))

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current=Depends(get_current_user)):
    user = service.delete_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"message": "Usuario eliminado correctamente"}
@router.get("/community/{community_id}", response_model=list[schemas.UserResponse])
def list_community_members(community_id: int, db: Session = Depends(get_db), current=Depends(get_current_user)):
    # Verificación de seguridad: si es líder, solo puede ver su propia comunidad
    if current.rol_id == 3 and current.community_id != community_id:
        raise HTTPException(
            status_code=403, 
            detail="No tienes permisos para ver los miembros de otra comunidad"
        )
    return service.get_all_by_community(db, community_id)
