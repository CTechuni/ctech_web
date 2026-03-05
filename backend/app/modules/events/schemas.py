from pydantic import BaseModel
from typing import Optional
from datetime import date, time

class EventBase(BaseModel):
    title: str
    description_event: Optional[str] = None
    date_events: Optional[date] = None
    time_events: Optional[time] = None
    place: str
    url_form: str
    image: str
    status: str

class EventCreate(EventBase):
    created_by: Optional[int] = None

class EventResponse(EventBase):
    id_event: int
    created_by: Optional[int] = None

    class Config:
        orm_mode = True
