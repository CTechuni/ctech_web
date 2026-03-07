from sqlalchemy.orm import Session
from . import repository, schemas
from app.modules.auth.service import get_password_hash

def create_user(db: Session, user_data: schemas.UserCreate):
    user_dict = user_data.model_dump()
    user_dict["password_hash"] = get_password_hash(user_dict.pop("password"))
    return repository.create(db, user_dict)

def change_role(db: Session, user_id: int, new_role_id: int):
    return repository.update(db, user_id, {"rol_id": new_role_id})

def list_leaders(db: Session):
    # Suponiendo que el rol_id de Leader es 3 según tu lógica
    return repository.get_by_role(db, 3)

def update_user(db: Session, user_id: int, user_data: dict):
    return repository.update(db, user_id, user_data)

def delete_user(db: Session, user_id: int):
    return repository.delete(db, user_id)
