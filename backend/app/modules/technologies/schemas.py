from pydantic import BaseModel
from typing import Optional


class TechnologyBase(BaseModel):
    name: str
    description: Optional[str] = None


class TechnologyCreate(TechnologyBase):
    pass


class TechnologyResponse(TechnologyBase):
    id: int

    class Config:
        orm_mode = True
