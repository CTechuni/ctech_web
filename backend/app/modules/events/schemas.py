from pydantic import BaseModel
from datetime import date, time
from typing import Optional

class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    event_date: date
    event_time: Optional[time] = None
    event_type: Optional[str] = None   # "presencial" | "virtual"
    location: Optional[str] = None     # dirección o URL de reunión
    capacity: Optional[int] = None
    visibility: str = "publico"        # "publico" | "privado"
    community_id: Optional[int] = None
    image_url: Optional[str] = None

class EventCreate(EventBase):
    status: str = "pending"            # "draft" | "pending"

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    event_date: Optional[date] = None
    event_time: Optional[time] = None
    event_type: Optional[str] = None
    location: Optional[str] = None
    capacity: Optional[int] = None
    visibility: Optional[str] = None
    status: Optional[str] = None       # draft | pending (mentor puede cambiar)
    image_url: Optional[str] = None

class EventResponse(EventBase):
    id: int
    status: str = "pending"
    image_url: Optional[str] = None
    community_name: Optional[str] = None


    class Config:
        from_attributes = True
