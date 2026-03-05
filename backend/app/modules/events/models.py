from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.core.database import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    event_date = Column(DateTime, nullable=False)
    location = Column(String(255))
    image_url = Column(Text) # Para el link de Cloudinary
    created_at = Column(DateTime, server_default=func.now())
