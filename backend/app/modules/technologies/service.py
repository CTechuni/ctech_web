from sqlalchemy.orm import Session
from fastapi import HTTPException
from . import repository

def list_technologies(db: Session):
    return repository.get_all(db)

def add_technology(db: Session, tech_data):
    # 1. Limpiar espacios extra
    clean_name = tech_data.name.strip()
    
    # 2. Verificar si ya existe (sin importar mayúsculas/minúsculas)
    existing = repository.get_by_name(db, clean_name)
    if existing:
        raise HTTPException(
            status_code=400, 
            detail=f"La tecnología '{clean_name}' ya está registrada."
        )
    
    # 3. Guardar si todo está bien
    return repository.create(db, clean_name)