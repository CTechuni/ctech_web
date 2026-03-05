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

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

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

# Esquema para registro (basado en tu modelo User)
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name_user: Optional[str] = None
    rol_id: int = 2 # Por defecto estudiante

    @field_validator('password')
    @classmethod
    def check_password(cls, v):
        return validate_password_complexity(v)