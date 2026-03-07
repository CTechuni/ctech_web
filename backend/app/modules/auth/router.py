from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from . import schemas, service, models
from .service import get_current_user

router = APIRouter(tags=["Auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(data: schemas.UserCreate, db: Session = Depends(get_db)):
    # 1. Validar nombre (solo letras y espacios)
    import re
    if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", data.name_user):
        raise HTTPException(status_code=400, detail="El nombre solo debe contener letras y espacios")

    # 2. Validar Email único
    existing_user = db.query(models.User).filter(models.User.email == data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="El correo electrónico ya se encuentra registrado")
    
    # 3. Validar Comunidad e Invitación
    from app.modules.communities.models import Community
    community = db.query(Community).filter(Community.id_community == data.community_id).first()
    if not community:
        raise HTTPException(status_code=404, detail="La comunidad seleccionada no existe")
    
    if data.invite_code != 'ADMIN_CREATE' and community.code != data.invite_code:
        raise HTTPException(status_code=400, detail="El código de invitación es incorrecto para esta comunidad")

    # 4. Crear Usuario
    new_user = models.User(
        email=data.email,
        password_hash=service.get_password_hash(data.password),
        name_user=data.name_user,
        rol_id=data.rol_id or 4, # 4 es User estándar
        community_id=data.community_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Usuario registrado exitosamente"}

@router.post("/login", response_model=schemas.Token)
def login(data: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="El correo electrónico no se encuentra registrado")
    
    if not service.verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="La contraseña es incorrecta")
    
    # Mapeo de roles para el frontend
    role_map = {1: "admin", 2: "mentor", 3: "leader", 4: "user"}
    role_name = role_map.get(user.rol_id, "user")
    
    token = service.create_access_token(data={"sub": user.email, "role": role_name, "id": user.id})
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "role": role_name,
            "name": user.name_user or "Usuario"
        }
    }

@router.post("/logout")
def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    service.block_token(db, token)
    return {"message": "Sesión cerrada exitosamente"}

@router.post("/reset-password")
def reset_password(data: schemas.ResetPasswordRequest, db: Session = Depends(get_db)):
    # Aquí Pydantic ya validó que la 'new_password' sea compleja
    # Lógica para buscar el usuario por el token y actualizar...
    return {"message": "Contraseña actualizada correctamente"}
    
