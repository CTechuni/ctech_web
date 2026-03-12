from sqlalchemy.orm import Session
from . import repository

def get_admin_dashboard(db: Session):
    # Aquí podrías añadir lógica de promedios o crecimiento mensual
    return repository.get_counts(db)

def get_leader_dashboard(db: Session, community_id: int):
    return repository.get_community_counts(db, community_id)

