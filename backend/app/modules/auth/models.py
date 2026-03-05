from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Role(Base):
    __tablename__ = "roles"
    id_rol = Column(Integer, primary_key=True, index=True)
    name_rol = Column(String(50), nullable=False, unique=True)
    description_rol = Column(String(255))

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(150), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    name_user = Column(String(150))
    rol_id = Column(Integer, ForeignKey("roles.id_rol"))
    status = Column(String(50), default="active")
    is_email_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    role = relationship("Role")

class TokenBlocklist(Base):
    __tablename__ = "token_blocklist"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(Text, nullable=False, index=True)
    blacklisted_at = Column(DateTime, server_default=func.now())