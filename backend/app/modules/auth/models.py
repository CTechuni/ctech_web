from sqlalchemy import Column, Integer, Text, DateTime, func
from app.core.database import Base

# NOTA: No definas Role o User aquí para evitar redundancia. 
# Importamos desde users para que el namespace models.User sea válido.
from app.modules.users.models import User, Role

class TokenBlocklist(Base):
    __tablename__ = "token_blocklist"
    __table_args__ = {'extend_existing': True} # Para evitar errores al recargar el servidor
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(Text, nullable=False, index=True)
    blacklisted_at = Column(DateTime, server_default=func.now())