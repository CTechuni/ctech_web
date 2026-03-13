from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Role(Base):
    __tablename__ = "roles"
    __table_args__ = {'extend_existing': True}

    id_rol = Column(Integer, primary_key=True, index=True)
    name_rol = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    # Relación inversa: Un rol tiene muchos usuarios
    users = relationship("User", back_populates="role")

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(150), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    name_user = Column(String(150))
    rol_id = Column(Integer, ForeignKey("roles.id_rol")) 
    community_id = Column(Integer, ForeignKey("communities.id_community"), nullable=True)
    status = Column(String(50), default="active")
    is_email_verified = Column(Boolean, default=False)
    reset_token = Column(String(255), unique=True, nullable=True, index=True)
    reset_token_expires = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    last_login = Column(DateTime, nullable=True)

    # Relaciones
    role = relationship("Role", back_populates="users")
    profile = relationship("Profile", back_populates="user", uselist=False)

class Profile(Base):
    __tablename__ = "profiles"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    bio = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)
    avatar_url = Column(String(255), nullable=True)
    github_url = Column(String(255), nullable=True)
    linkedin_url = Column(String(255), nullable=True)

    # Relación con User
    user = relationship("User", back_populates="profile")