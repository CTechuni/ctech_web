import re
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional

# Función reutilizable para validar la complejidad exigida
def validate_password_complexity(value: str) -> str:
    if not (5 <= len(value) <= 13):
        raise ValueError('La contraseña debe tener entre 5 y 13 caracteres.')
    if not re.search(r"[a-z]", value):
        raise ValueError('Debe incluir al menos una letra minúscula.')
    if not re.search(r"[A-Z]", value):
        raise ValueError('Debe incluir al menos una letra mayúscula.')
    if not re.search(r"\d", value):
        raise ValueError('Debe incluir al menos un número.')
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
        raise ValueError('Debe incluir al menos un signo especial (ej: !@#$).')
    return value

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserInfo(BaseModel):
    id: int
    email: str
    role: str
    name_user: str
    community_name: Optional[str] = "Sin Comunidad"

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserInfo

class TokenData(BaseModel):
    email: Optional[str] = None

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

    @field_validator('new_password')
    @classmethod
    def check_password(cls, v):
        return validate_password_complexity(v)

# Esquema para registro (basado en el modelo User)
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name_user: str = Field(..., min_length=4, max_length=65) # Nombre completo
    community_id: int
    invite_code: str
    rol_id: Optional[int] = 4 # Por defecto User (estudiante)

    @field_validator('password')
    @classmethod
    def check_password(cls, v):
        return validate_password_complexity(v)