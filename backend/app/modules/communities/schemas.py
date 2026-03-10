from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CommunityBase(BaseModel):
    name_community: str
    description_community: Optional[str] = None
    status_community: str
    code: str
    access_code: Optional[str] = None
    logo_url: Optional[str] = None
    leader_id: Optional[int] = None

class CommunityCreate(CommunityBase):
    pass

class CommunityUpdate(BaseModel):
    name_community: Optional[str] = None
    description_community: Optional[str] = None
    status_community: Optional[str] = None
    code: Optional[str] = None
    access_code: Optional[str] = None
    logo_url: Optional[str] = None
    leader_id: Optional[int] = None

class CommunityResponse(CommunityBase):
    id_community: int
    member_count: int = 0
    leader_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class CommunityPublicResponse(BaseModel):
    id_community: int
    name_community: str
    code: str
    logo_url: Optional[str] = None

    class Config:
        from_attributes = True
        