from sqlalchemy import Column, Integer, String, Text, Date, Time
from app.core.database import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True, name="id_event")
    title = Column(String(255), nullable=False)
    description = Column(Text, name="description_event")
    event_date = Column(Date, name="date_events")
    event_time = Column(Time, name="time_events")
    location = Column(String(255), name="place")
    image_url = Column(Text, name="image")
    status = Column(String(50), default="pending")   # draft | pending | approved | rejected
    visibility = Column(String(20), default="publico") # publico | privado
    event_type = Column(String(50), name="type_event")
    capacity = Column(Integer)
    community_id = Column(Integer)
    mentor_id = Column(Integer)
    course_id = Column(Integer)
