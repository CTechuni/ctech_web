from sqlalchemy.orm import Session
from . import repository

def get_admin_dashboard(db: Session):
    # Aquí podrías añadir lógica de promedios o crecimiento mensual
    return repository.get_counts(db)