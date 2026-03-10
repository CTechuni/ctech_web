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

@router.patch("/me/password")
def change_my_password(data: schemas.ChangePasswordRequest, db: Session = Depends(get_db), current=Depends(get_current_user)):
    from app.modules.auth.service import verify_password, get_password_hash
    if not verify_password(data.current_password, current.password_hash):
        raise HTTPException(status_code=400, detail="La contraseña actual es incorrecta")
    from . import repository
    repository.update(db, current.id, {"password_hash": get_password_hash(data.new_password)})
    return {"message": "Contraseña actualizada correctamente"}

@router.patch("/{user_id}/promote")
def promote(user_id: int, req: schemas.UserPromoteRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current=Depends(get_current_user)):
    if current.rol_id not in [1, 3]:
        raise HTTPException(status_code=403, detail="Solo el administrador o el líder pueden promover usuarios a mentor")

    target = service.get_user(db, user_id)
    if not target:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # El líder solo puede promover usuarios de su propia comunidad
    if current.rol_id == 3:
        if target.community_id != current.community_id:
            raise HTTPException(status_code=403, detail="Solo puedes promover usuarios de tu comunidad")
        if target.rol_id != 4:
            raise HTTPException(status_code=400, detail="Solo puedes promover usuarios estándar a mentor")

    user = service.change_role(db, user_id, 2, specialty_id=req.specialty_id)

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
    if current.rol_id not in [1, 3]:
        raise HTTPException(status_code=403, detail="Solo el administrador o el líder pueden revocar el rol de mentor")

    target = service.get_user(db, user_id)
    if not target:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # El líder solo puede designar mentores de su propia comunidad
    if current.rol_id == 3:
        if target.community_id != current.community_id:
            raise HTTPException(status_code=403, detail="Solo puedes designar mentores de tu comunidad")
        if target.rol_id != 2:
            raise HTTPException(status_code=400, detail="El usuario seleccionado no es mentor")

    user = service.change_role(db, user_id, 4)

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

@router.delete("/me")
def delete_me(db: Session = Depends(get_db), current=Depends(get_current_user)):
    service.delete_user(db, current.id)
    return {"message": "Cuenta eliminada correctamente"}

@router.get("/leaders", response_model=list[schemas.UserResponse])
def get_leaders(db: Session = Depends(get_db), current=Depends(get_current_user)):
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
