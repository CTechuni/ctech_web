from pydantic import BaseModel
from typing import Optional


class SpecialtyBase(BaseModel):
    name: str
    description: Optional[str] = None


class SpecialtyCreate(SpecialtyBase):
    pass


class SpecialtyResponse(SpecialtyBase):
    id: int

    class Config:
        orm_mode = True
