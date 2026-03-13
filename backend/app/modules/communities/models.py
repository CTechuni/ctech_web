from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from app.core.database import Base

class Community(Base):
    __tablename__ = "communities"

    id_community = Column(Integer, primary_key=True, index=True)
    name_community = Column(String(150), nullable=False)
    description_community = Column(Text)
    status_community = Column(String(150), nullable=False)
    code = Column(String(50), nullable=False, unique=True)
    access_code = Column(String(50), unique=True)
    logo_url = Column(String(255))
    leader_id = Column(Integer, ForeignKey("users.id"), nullable=True) # <--- Added leader ID
    created_at = Column(DateTime, server_default=func.now())
    