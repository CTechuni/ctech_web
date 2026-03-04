# Aislamiento de Errores: Al forzar client_encoding: utf8, le ordenas a PostgreSQL que te hable en un idioma que Python siempre entiende.

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import get_settings

settings = get_settings()

# Añadimos el argumento de conexión para evitar el error de decodificación
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"client_encoding": "utf8"} 
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()