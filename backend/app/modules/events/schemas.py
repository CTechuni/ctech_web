from pydantic import BaseModel
from datetime import datetime, date, time
from typing import Optional

class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    event_date: date
    location: Optional[str] = None
    event_time: Optional[time] = None
    event_type: Optional[str] = None
    capacity: Optional[int] = None
    community_id: Optional[int] = None

class EventCreate(EventBase):
    pass

class EventResponse(EventBase):
    id: int
    image_url: Optional[str] = None
    community_name: Optional[str] = None

    class Config:
        from_attributes = True

