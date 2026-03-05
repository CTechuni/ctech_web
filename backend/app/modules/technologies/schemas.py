from pydantic import BaseModel, Field

class TechnologyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)

class TechnologyCreate(TechnologyBase):
    pass

class TechnologyResponse(TechnologyBase):
    id: int

    class Config:
        from_attributes = True