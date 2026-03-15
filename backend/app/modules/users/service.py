from sqlalchemy.orm import Session
from fastapi import HTTPException
from . import repository, schemas, models
from app.modules.auth.service import get_password_hash
from app.modules.communities.models import Community
from app.modules.notifications import service as notification_service

def create_user(db: Session, user_data: schemas.UserCreate):
    user_dict = user_data.model_dump()
    user_dict["password_hash"] = get_password_hash(user_dict.pop("password"))
    if user_dict.get("rol_id") == 3 and user_dict.get("community_id"):
        validate_community_available(db, user_dict["community_id"])
    user = repository.create(db, user_dict)
    if user.rol_id == 3 and user.community_id:
        sync_community_leader(db, user.community_id, user.id)
    return user

def change_role(db: Session, user_id: int, new_role_id: int):
    user = repository.get_by_id(db, user_id)
    if not user:
        return None
        
    old_role_id = user.rol_id
    
    # Si deja de ser líder, limpiar la comunidad
    if old_role_id == 3 and new_role_id != 3:
        db.query(Community).filter(Community.leader_id == user_id).update({"leader_id": None})
        db.commit()
    
    update_data = {"rol_id": new_role_id}
    updated_user = repository.update(db, user_id, update_data)
    
    # Si pasa a ser líder y tiene comunidad, validar y sincronizar
    if new_role_id == 3 and updated_user.community_id:
        validate_community_available(db, updated_user.community_id, exclude_leader_id=user_id)
        sync_community_leader(db, updated_user.community_id, user_id)
        
    return updated_user

def list_leaders(db: Session, available: bool = False):
    return repository.get_leaders_enriched(db, only_available=available)

def update_user(db: Session, user_id: int, user_data: dict):
    if "email" in user_data and user_data["email"]:
        from .models import User
        existing = db.query(User).filter(User.email == user_data["email"], User.id != user_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="El correo electrónico ya se encuentra registrado por otro usuario")

    # Fetch early to use old values in validations
    user = repository.get_by_id(db, user_id)
    old_role_id = user.rol_id if user else None
    old_community_id = user.community_id if user else None

    new_rol = user_data.get("rol_id", old_role_id)
    new_comm = user_data.get("community_id", old_community_id)

    # Comunidad → solo un líder:
    # Validar cuando cambia community_id O cuando el usuario pasa a ser líder (con comunidad ya asignada)
    if new_comm and ("community_id" in user_data or (new_rol == 3 and old_role_id != 3)):
        validate_community_available(db, new_comm, exclude_leader_id=user_id)

    # Líder → solo una comunidad:
    # Bloquear si ya es líder de una comunidad diferente a la nueva
    if new_rol == 3 and old_role_id == 3 and old_community_id and new_comm and old_community_id != new_comm:
        raise HTTPException(
            status_code=400,
            detail="Este usuario ya es líder de otra comunidad. Debe ser removido primero."
        )

    # Si deja de ser líder o cambia de comunidad, limpiar referencia antigua
    if old_role_id == 3:
        if new_rol != 3 or (new_comm != old_community_id and new_comm is not None):
            db.query(Community).filter(Community.leader_id == user_id).update({"leader_id": None})
            db.commit()

    user = repository.update(db, user_id, user_data)

    # Si es/pasa a ser líder, sincronizar con la nueva comunidad
    if user and user.rol_id == 3:
        if "community_id" in user_data or "rol_id" in user_data:
            if user.community_id:
                sync_community_leader(db, user.community_id, user.id)
    return user

def validate_community_available(db: Session, community_id: int, exclude_leader_id: int = None):
    """Raises 400 if the community already has a different leader."""
    community = db.query(Community).filter(Community.id_community == community_id).first()
    if not community:
        raise HTTPException(status_code=404, detail="Comunidad no encontrada")
    # Check via users table: any other leader assigned to this community
    existing = db.query(models.User).filter(
        models.User.community_id == community_id,
        models.User.rol_id == 3
    ).first()
    if existing and existing.id != exclude_leader_id:
        raise HTTPException(
            status_code=400,
            detail=f"La comunidad '{community.name_community}' ya tiene un líder asignado."
        )
    # Also check community.leader_id
    if community.leader_id and community.leader_id != exclude_leader_id:
        raise HTTPException(
            status_code=400,
            detail=f"La comunidad '{community.name_community}' ya tiene un líder asignado."
        )

def sync_community_leader(db: Session, community_id: int, leader_id: int):
    if community_id:
        db.query(Community).filter(Community.id_community == community_id).update({"leader_id": leader_id})
        db.commit()

def delete_user(db: Session, user_id: int):
    # If user is a leader, clear the reference in the community first
    db.query(Community).filter(Community.leader_id == user_id).update({"leader_id": None})
    db.commit()
    return repository.delete(db, user_id)

def get_all(db: Session):
    return repository.get_all(db)

def get_paginated(db: Session, page: int, limit: int, role_id: int = None, search: str = None):
    users = repository.get_paginated(db, page, limit, role_id, search)
    total = repository.get_count(db, role_id, search)
    return {"users": users, "total": total}

def get_user(db: Session, user_id: int):
    return repository.get_by_id(db, user_id)

def get_all_by_community(db: Session, community_id: int):
    return repository.get_by_community(db, community_id)
