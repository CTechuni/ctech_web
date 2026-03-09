from sqlalchemy.orm import Session
from . import repository, schemas

def list_communities(db: Session, current_user=None):
    leader_id = None
    if current_user and current_user.rol_id == 3: # 3 es el rol de líder
        leader_id = current_user.id
    return repository.get_all(db, leader_id=leader_id)

def create_community(db: Session, community: schemas.CommunityCreate):
    return repository.create(db, community)

def update_community(db: Session, community_id: int, data: schemas.CommunityUpdate):
    return repository.update(db, community_id, data.model_dump(exclude_unset=True))

def delete_community(db: Session, community_id: int):
    return repository.delete(db, community_id)
    
def list_with_logo(db: Session):
    return repository.get_with_logo(db)