from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.auth.router import get_current_user
from . import schemas, service

router = APIRouter(prefix="/users", tags=["Users"])

# Público
# Protegido
@router.get("/", response_model=schemas.UserPaginationResponse)
def list_users(page: int = 1, limit: int = 6, role: str = "all", search: str = None, db: Session = Depends(get_db), current=Depends(get_current_user)):
    role_id = None
    if role != "all":
        role_map = {"admin": 1, "mentor": 2, "leader": 3, "user": 4}
        role_id = role_map.get(role.lower())
        
    return service.get_paginated(db, page, limit, role_id, search)

@router.get("/me", response_model=schemas.UserResponse)
def get_me(current=Depends(get_current_user), db: Session = Depends(get_db)):
    return service.get_user(db, current.id)

@router.patch("/{user_id}/promote")
def promote(user_id: int, req: schemas.UserPromoteRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current=Depends(get_current_user)):
    user = service.change_role(db, user_id, 2, specialty_id=req.specialty_id) # 2 para Mentor
    
    # Enviar Email de Promoción
    from app.core.email_service import email_service
    from app.modules.communities.models import Community
    from app.modules.specialties.models import Specialty
    
    community = db.query(Community).filter(Community.id_community == user.community_id).first()
    specialty = db.query(Specialty).filter(Specialty.id == req.specialty_id).first()
    
    background_tasks.add_task(
        email_service.send_promotion_email,
        recipient_email=user.email,
        name_user=user.name_user,
        specialty=specialty.name if specialty else "General",
        name_community=community.name_community if community else "CTech"
    )
    return user

@router.patch("/{user_id}/demote")
def demote(user_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current=Depends(get_current_user)):
    user = service.change_role(db, user_id, 4) # 4 para User estándar
    
    # Enviar Email de Designación
    from app.core.email_service import email_service
    from app.modules.communities.models import Community
    
    community = db.query(Community).filter(Community.id_community == user.community_id).first()
    
    background_tasks.add_task(
        email_service.send_designation_email,
        recipient_email=user.email,
        name_user=user.name_user,
        name_community=community.name_community if community else "CTech"
    )
    return user

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
