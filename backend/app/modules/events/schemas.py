from pydantic import BaseModel, field_validator
from datetime import date, time
from typing import Optional, Literal

class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    event_date: date
    event_time: Optional[time] = None
    event_type: Optional[Literal["presencial", "virtual"]] = None
    location: Optional[str] = None     # dirección o URL de reunión
    capacity: Optional[int] = None
    visibility: Literal["publico", "privado"] = "publico"
    community_id: Optional[int] = None
    image_url: Optional[str] = None

    @field_validator("capacity")
    @classmethod
    def capacity_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("La capacidad debe ser mayor a 0")
        return v

class EventCreate(EventBase):
    status: Literal["draft", "pending"] = "pending"
    creator_id: Optional[int] = None

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    event_date: Optional[date] = None
    event_time: Optional[time] = None
    event_type: Optional[Literal["presencial", "virtual"]] = None
    location: Optional[str] = None
    capacity: Optional[int] = None
    visibility: Optional[Literal["publico", "privado"]] = None
    image_url: Optional[str] = None
    # status excluido — los cambios de estado solo van por /approve y /reject

    @field_validator("capacity")
    @classmethod
    def capacity_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("La capacidad debe ser mayor a 0")
        return v

class EventResponse(EventBase):
    id: int
    status: str = "pending"
    image_url: Optional[str] = None
    community_name: Optional[str] = None
    registered_count: Optional[int] = None

    class Config:
        from_attributes = True
