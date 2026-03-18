from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.auth.router import get_current_user
from . import schemas, service

router = APIRouter(prefix="/users", tags=["Users"])

# Público
# Protegido
@router.post("/", response_model=schemas.UserResponse)
def create_user(data: schemas.UserCreate, db: Session = Depends(get_db), current=Depends(get_current_user)):
    if current.rol_id != 1:
        raise HTTPException(status_code=403, detail="Solo el administrador puede crear usuarios directamente")
    return service.create_user(db, data)

@router.get("/", response_model=schemas.UserPaginationResponse)
def list_users(page: int = 1, limit: int = 6, role: str = "all", search: str = None, db: Session = Depends(get_db), current=Depends(get_current_user)):
    # Líder: solo ve los miembros de su propia comunidad
    if current.rol_id == 3:
        if not current.community_id:
            return {"users": [], "total": 0}
        members = service.get_all_by_community(db, current.community_id)
        return {"users": members, "total": len(members)}

    # Solo admin puede ver el listado global
    if current.rol_id != 1:
        raise HTTPException(status_code=403, detail="No tienes permisos para ver el listado de usuarios")

    role_id = None
    if role != "all":
        role_map = {"admin": 1, "leader": 3, "user": 4}
        role_id = role_map.get(role.lower())

    return service.get_paginated(db, page, limit, role_id, search)

@router.get("/me", response_model=schemas.UserResponse)
def get_me(current=Depends(get_current_user), db: Session = Depends(get_db)):
    return service.get_user(db, current.id)

@router.patch("/me", response_model=schemas.UserResponse)
def update_me(data: schemas.UserUpdate, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current=Depends(get_current_user)):
    old_email = current.email
    old_name  = current.name_user
    update_data = data.model_dump(exclude_unset=True)
    updated = service.update_user(db, current.id, update_data)

    name_changed  = "name_user" in update_data and update_data["name_user"] != old_name
    email_changed = "email" in update_data and update_data["email"] != old_email

    if name_changed or email_changed:
        from app.core.email_service import email_service
        recipient = updated.email  # nuevo email si cambió, mismo si solo nombre
        background_tasks.add_task(
            email_service.send_profile_update_email,
            recipient_email=recipient,
            name_user=updated.name_user or old_name,
            name_changed=name_changed,
            email_changed=email_changed,
            new_email=updated.email if email_changed else None
        )

    return updated

@router.patch("/me/password")
def change_my_password(data: schemas.ChangePasswordRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current=Depends(get_current_user)):
    from app.modules.auth.service import verify_password, get_password_hash
    if not verify_password(data.current_password, current.password_hash):
        raise HTTPException(status_code=400, detail="La contraseña actual es incorrecta")
    from . import repository
    repository.update(db, current.id, {"password_hash": get_password_hash(data.new_password)})
    from app.core.email_service import email_service
    background_tasks.add_task(
        email_service.send_password_change_email,
        recipient_email=current.email,
        name_user=current.name_user or current.email
    )
    return {"message": "Contraseña actualizada correctamente"}

@router.delete("/me")
def delete_me(db: Session = Depends(get_db), current=Depends(get_current_user)):
    if current.rol_id == 1:
        raise HTTPException(status_code=403, detail="El administrador no puede eliminar su propia cuenta")
    service.delete_user(db, current.id)
    return {"message": "Cuenta eliminada correctamente"}

@router.get("/leaders", response_model=list[schemas.UserResponse])
def get_leaders(available: bool = False, db: Session = Depends(get_db), current=Depends(get_current_user)):
    return service.list_leaders(db, available=available)

@router.patch("/{user_id}/role", response_model=schemas.UserResponse)
def change_user_role(user_id: int, data: schemas.ChangeRoleRequest, db: Session = Depends(get_db), current=Depends(get_current_user)):
    if current.rol_id != 1:
        raise HTTPException(status_code=403, detail="Solo el administrador puede cambiar roles")
    user = service.change_role(db, user_id, data.rol_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

@router.patch("/{user_id}", response_model=schemas.UserResponse)
def update_user(user_id: int, data: schemas.UserUpdate, db: Session = Depends(get_db), current=Depends(get_current_user)):
    # exclude_unset=True ensures only the fields sent in the request are included
    return service.update_user(db, user_id, data.model_dump(exclude_unset=True))

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current=Depends(get_current_user)):
    if current.rol_id != 1:
        raise HTTPException(status_code=403, detail="Solo el administrador puede eliminar usuarios")
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
