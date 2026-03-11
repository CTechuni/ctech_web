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
    # Sync leader
    if db_comm.leader_id:
        db.query(User).filter(User.id == db_comm.leader_id).update({
            "community_id": db_comm.id_community,
            "rol_id": 3 # Forzar a rol líder
        })
        db.commit()
    return db_comm

def update_community(db: Session, community_id: int, data: schemas.CommunityUpdate):
    update_data = data.model_dump(exclude_unset=True)
    db_comm = repository.update(db, community_id, update_data)
    
    # Sync leader if updated
    if "leader_id" in update_data and update_data["leader_id"]:
        db.query(User).filter(User.id == update_data["leader_id"]).update({
            "community_id": community_id,
            "rol_id": 3
        })
        db.commit()
    return db_comm

def delete_community(db: Session, community_id: int):
    return repository.delete(db, community_id)
    
def list_with_logo(db: Session):
    return repository.get_with_logo(db)