from sqlalchemy.orm import Session
from fastapi import HTTPException
from . import repository, schemas, models
from app.modules.auth.service import get_password_hash
from app.modules.communities.models import Community

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
    return repository.update(db, user_id, {"rol_id": new_role_id})

def list_leaders(db: Session):
    return repository.get_leaders_enriched(db)

def list_mentors(db: Session):
    return repository.get_mentors_enriched(db)

def update_user(db: Session, user_id: int, user_data: dict):
    if "community_id" in user_data and user_data["community_id"]:
        validate_community_available(db, user_data["community_id"], exclude_leader_id=user_id)
    user = repository.update(db, user_id, user_data)
    if user and user.rol_id == 3 and "community_id" in user_data:
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
    return repository.delete(db, user_id)

def get_all(db: Session):
    return repository.get_all(db)

def get_paginated(db: Session, page: int, limit: int):
    users = repository.get_paginated(db, page, limit)
    total = repository.get_count(db)
    return {"users": users, "total": total}

def get_user(db: Session, user_id: int):
    return repository.get_by_id(db, user_id)

def get_all_by_community(db: Session, community_id: int):
    return repository.get_by_community(db, community_id)
