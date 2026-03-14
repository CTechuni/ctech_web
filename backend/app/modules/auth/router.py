from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from . import schemas, service, models
from .service import get_current_user, oauth2_scheme
from app.modules.communities.models import Community
from app.modules.users.models import Profile
from app.core.email_service import email_service
from app.modules.notifications.service import add_notification
from fastapi.security import HTTPAuthorizationCredentials
import re
import secrets
from datetime import datetime, timedelta

router = APIRouter(tags=["Auth"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(data: schemas.UserCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # 1. Validar nombre (solo letras y espacios)
    import re
    if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", data.name_user):
        raise HTTPException(status_code=400, detail="El nombre solo debe contener letras y espacios")

    # 2. Validar Email único
    existing_user = db.query(models.User).filter(models.User.email == data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="El correo electrónico ya se encuentra registrado")
    
    # 3. Validar Comunidad e Invitación
    community = db.query(Community).filter(Community.id_community == data.community_id).first()
    if not community:
        raise HTTPException(status_code=404, detail="La comunidad seleccionada no existe")
    
    if data.invite_code != 'ADMIN_CREATE' and community.code != data.invite_code:
        raise HTTPException(status_code=400, detail="El código de invitación es incorrecto para esta comunidad")

    # 4. Crear Usuario (registro público siempre crea rol estándar = 4)
    new_user = models.User(
        email=data.email,
        password_hash=service.get_password_hash(data.password),
        name_user=data.name_user,
        rol_id=4,  # Público siempre es User estándar
        community_id=data.community_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 4.1. Si es líder (3), sincronizar con la comunidad
    if new_user.rol_id == 3 and new_user.community_id:
        db.query(Community).filter(Community.id_community == new_user.community_id).update({"leader_id": new_user.id})
        db.commit()

    # 5. Vincular Perfil vacío automáticamente
    new_profile = Profile(user_id=new_user.id)
    db.add(new_profile)
    db.commit()

    # 6. Enviar Correo de Bienvenida (Background Task)
    
    background_tasks.add_task(
        email_service.send_welcome_email, 
        recipient_email=new_user.email,
        name_user=new_user.name_user,
        name_community=community.name_community
    )

    # 7. Notificaciones
    if new_user.community_id:
        comm = db.query(Community).filter(Community.id_community == new_user.community_id).first()
        if comm and comm.leader_id:
            add_notification(
                db, 
                "Nuevo Miembro", 
                f"El usuario {new_user.name_user} se ha unido a tu comunidad: {comm.name_community}", 
                "info", 
                recipient_id=comm.leader_id
            )

    return {"message": "Usuario registrado exitosamente"}

@router.post("/token", include_in_schema=False)
def token_for_swagger(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Endpoint exclusivo para autenticación en Swagger UI (OAuth2PasswordFlow)."""
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not service.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    role_map = {1: "admin", 3: "leader", 4: "user"}
    role_name = role_map.get(user.rol_id, "user")
    token = service.create_access_token(data={"sub": user.email, "role": role_name, "id": user.id})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/login", response_model=schemas.Token)
def login(data: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="El correo electrónico no se encuentra registrado")
    
    if not service.verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="La contraseña es incorrecta")
    
    # Mapeo de roles para el frontend
    role_map = {1: "admin", 3: "leader", 4: "user"}
    role_name = role_map.get(user.rol_id, "user")
    
    token = service.create_access_token(data={"sub": user.email, "role": role_name, "id": user.id})

    # Registrar último login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Obtener nombre de la comunidad si existe
    community_name = "Sin Comunidad"
    if user.community_id:
        community = db.query(Community).filter(Community.id_community == user.community_id).first()
        if community:
            community_name = community.name_community

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "role": role_name,
            "rol_id": user.rol_id,
            "name_user": user.name_user or "Usuario",
            "community_id": user.community_id,
            "community_name": community_name,
        }
    }

@router.post("/logout")
def logout(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    service.block_token(db, credentials.credentials)
    return {"message": "Sesión cerrada exitosamente"}

from . import repository

@router.post("/forgot-password")
def forgot_password(data: schemas.ForgotPasswordRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if not user:
        # Por seguridad en producción, a veces se prefiere no revelar si el correo existe.
        # Pero aquí mantendremos la lógica actual o similar.
        raise HTTPException(
            status_code=400,
            detail="Si el correo está registrado, recibirás un enlace."
        )
    
    # Generar token seguro
    token = secrets.token_urlsafe(32)
    expires = datetime.utcnow() + timedelta(hours=1)
    
    repository.set_reset_token(db, user.id, token, expires)
    background_tasks.add_task(
        email_service.send_reset_password_email,
        recipient_email=user.email,
        name_user=user.name_user,
        token=token
    )
    
    return {"message": "Se ha enviado un enlace de recuperación a tu correo electrónico."}

@router.patch("/reset-password")
def reset_password(data: schemas.ResetPasswordRequest, db: Session = Depends(get_db)):
    # 1. Buscar usuario por token y email
    user = repository.get_user_by_reset_token(db, token=data.token)

    if not user or user.email != data.email:
        raise HTTPException(
            status_code=400,
            detail="El enlace de recuperación es inválido o ha expirado."
        )

    # 2. Generar hash
    new_hashed_password = service.get_password_hash(data.new_password)

    # 3. Actualizar (update_user_password ya limpia el token)
    updated_user = repository.update_user_password(db, user.id, new_hashed_password)

    if updated_user:
        return {"message": "Contraseña actualizada correctamente"}
    else:
        raise HTTPException(status_code=500, detail="Error interno al actualizar la contraseña")
    
