from sqlalchemy.orm import Session
from . import models
from datetime import datetime

# --- Funciones de Usuario ---

def get_user_by_email(db: Session, email: str):
    """Busca un usuario por su correo electrónico."""
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user_data: dict):
    """
    Registra un nuevo usuario en la base de datos.
    user_data debe contener: email, password_hash, name_user y rol_id.
    """
    db_user = models.User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_password(db: Session, user_id: int, new_hashed_password: str):
    """Actualiza la contraseña de un usuario existente y limpia el token de reset."""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db_user.password_hash = new_hashed_password
        db_user.reset_token = None
        db_user.reset_token_expires = None
        db.commit()
        db.refresh(db_user)
        return db_user
    return None

def set_reset_token(db: Session, user_id: int, token: str, expires: datetime):
    """Guarda un token de recuperación para un usuario."""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db_user.reset_token = token
        db_user.reset_token_expires = expires
        db.commit()
        db.refresh(db_user)
        return db_user
    return None

def get_user_by_reset_token(db: Session, token: str):
    """Busca un usuario por su token de recuperación activo."""
    return db.query(models.User).filter(
        models.User.reset_token == token,
        models.User.reset_token_expires > datetime.utcnow()
    ).first()

# --- Funciones de Seguridad (Logout) ---

def add_token_to_blocklist(db: Session, token: str):
    """
    Registra un token en la lista negra para invalidar la sesión.
    """
    db_token = models.TokenBlocklist(
        token=token, 
        blacklisted_at=datetime.utcnow()
    )
    db.add(db_token)
    db.commit()
    return db_token

def is_token_blacklisted(db: Session, token: str):
    """Verifica si un token ya ha sido invalidado."""
    return db.query(models.TokenBlocklist).filter(models.TokenBlocklist.token == token).first() is not None

# --- Funciones de Roles ---

def get_role_by_id(db: Session, role_id: int):
    """Obtiene los detalles de un rol específico."""
    return db.query(models.Role).filter(models.Role.id_rol == role_id).first()