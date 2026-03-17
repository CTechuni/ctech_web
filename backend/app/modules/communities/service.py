from sqlalchemy.orm import Session
from . import repository, schemas
from app.modules.users.models import User

def list_communities(db: Session, current_user=None):
    leader_id = None
    if current_user and current_user.rol_id == 3: # 3 es el rol de líder
        leader_id = current_user.id
    return repository.get_all(db, leader_id=leader_id)

def create_community(db: Session, community: schemas.CommunityCreate):
    db_comm = repository.create(db, community)
    # Sync leader using the centralized logic
    if db_comm.leader_id:
        from app.modules.users.service import sync_community_leader
        sync_community_leader(db, db_comm.id_community, db_comm.leader_id)
    return db_comm

def update_community(db: Session, community_id: int, data: schemas.CommunityUpdate):
    update_data = data.model_dump(exclude_unset=True)
    
    # 1. Perform main community update
    db_comm = repository.update(db, community_id, update_data)
    
    # 2. Sync leader if provided (Centralized logic handles cleanup)
    if "leader_id" in update_data:
        from app.modules.users.service import sync_community_leader
        sync_community_leader(db, community_id, update_data["leader_id"])
        
    return db_comm

def delete_community(db: Session, community_id: int):
    return repository.delete(db, community_id)
    
def list_with_logo(db: Session):
    return repository.get_with_logo(db)