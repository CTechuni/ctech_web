from pydantic import BaseModel
from typing import Optional

class CommunityBase(BaseModel):
    name_community: str
    description_community: Optional[str] = None
    status_community: str
    code: str
    access_code: Optional[str] = None

class CommunityCreate(CommunityBase):
    pass

class CommunityResponse(CommunityBase):
    id_community: int

    class Config:
        orm_mode = True
