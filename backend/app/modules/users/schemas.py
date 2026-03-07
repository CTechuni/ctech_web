from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    name_user: Optional[str] = None

class UserCreate(UserBase):
    password: str
    rol_id: int

class UserUpdate(BaseModel):
    name_user: Optional[str] = None
    email: Optional[EmailStr] = None
    status: Optional[str] = None
    community_id: Optional[int] = None

class UserResponse(UserBase):
    id: int
    rol_id: int
    community_id: Optional[int] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
