from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.database import get_db
from app.core.config import get_settings
from . import models, repository

# Configuración de seguridad
settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.ALGORITHM
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")

# --- Funciones de Contraseña ---

def verify_password(plain_password, hashed_password):
    # Bcrypt has a physical limit of 72 characters.
    if len(plain_password) > 72:
        return False
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    if len(password) > 72:
        raise ValueError("La contraseña excede el límite permitido por el sistema de seguridad (72 caracteres).")
    return pwd_context.hash(password)

# --- Funciones de Token (JWT) ---

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def block_token(db: Session, token: str):
    """Registra el token en la tabla de bloqueo."""
    repository.add_token_to_blocklist(db, token)

# --- LA PIEZA QUE FALTA: Validación de Usuario Actual ---

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Esta función es la que pedía el error. 
    Valida el token y devuelve el usuario logueado.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar el acceso",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if repository.is_token_blacklisted(db, token):
        raise credentials_exception

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = repository.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user = Depends(get_current_user)):
    """
    Verifica que el usuario actual esté activo.
    """
    if current_user.status != "active":
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    return current_user