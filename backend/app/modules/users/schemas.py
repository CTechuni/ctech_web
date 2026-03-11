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

class ProfileResponse(BaseModel):
    bio: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None

    class Config:
        from_attributes = True

class UserResponse(UserBase):
    id: int
    rol_id: int
    community_id: Optional[int] = None
    community_name: Optional[str] = None
    community_code: Optional[str] = None
    member_count: Optional[int] = None
    status: str
    created_at: datetime
    profile: Optional[ProfileResponse] = None

class UserPaginationResponse(BaseModel):
    users: list[UserResponse]
    total: int


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
