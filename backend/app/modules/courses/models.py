from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, JSON, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    is_premium = Column(Boolean, default=False)
    technologies = Column(JSON, default=[]) 
    content_links = Column(JSON)
    thumbnail_url = Column(Text)
    mentor_id = Column(Integer, ForeignKey("users.id"))
    community_id = Column(Integer, ForeignKey("communities.id_community"))
    specialty_id = Column(Integer, ForeignKey("specialties.id"))
    created_at = Column(DateTime, server_default=func.now())

    # Relaciones
    mentor = relationship("app.modules.users.models.User")
    specialty = relationship("app.modules.specialties.models.Specialty")

    @property
    def mentor_name(self):
        return self.mentor.name_user if self.mentor else None

    @property
    def specialty_name(self):
        return self.specialty.name if self.specialty else None
