from pydantic import BaseModel

class SpecialtyBase(BaseModel):
    name: str

class SpecialtyCreate(SpecialtyBase):
    pass

class SpecialtyResponse(SpecialtyBase):
    id: int

    class Config:
        from_attributes = True