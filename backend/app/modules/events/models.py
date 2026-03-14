from sqlalchemy import Column, Integer, String, Text, Date, Time, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from app.core.database import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True, name="id_event")
    title = Column(String(255), nullable=False)
    description = Column(Text, name="description_event")
    event_date = Column(Date, name="date_events")
    event_time = Column(Time, name="time_events")
    location = Column(Text, name="place")
    image_url = Column(Text, name="image")
    status = Column(String(50), default="pending")   # draft | pending | approved | rejected
    visibility = Column(String(20), default="publico") # publico | privado
    event_type = Column(String(50), name="type_event")
    capacity = Column(Integer)
    community_id = Column(Integer, ForeignKey("communities.id_community"))
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=True)


class EventRegistration(Base):
    __tablename__ = "event_registrations"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id_event"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    registered_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("event_id", "user_id", name="uq_event_user"),
    )
