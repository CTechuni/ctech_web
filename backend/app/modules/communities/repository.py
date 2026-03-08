from sqlalchemy.orm import Session, aliased
from sqlalchemy import func, or_, and_
from app.modules.users.models import User
from . import models, schemas

def get_all(db: Session, leader_id: int = None):
    # Optimized query with joins for members and leader information
    Member = aliased(User)
    Leader = aliased(User)
    
    # We join Leader on:
    # 1. Direct match with Community.leader_id
    # 2. OR User with role 'leader' (3) assigned to this community_id
    leader_join_cond = or_(
        models.Community.leader_id == Leader.id,
        and_(Leader.rol_id == 3, Leader.community_id == models.Community.id_community)
    )

    query = db.query(
        models.Community,
        func.count(Member.id).label("member_count"),
        Leader.name_user.label("leader_name_direct"),
        Leader.email.label("leader_email")
    ).outerjoin(Member, Member.community_id == models.Community.id_community)\
     .outerjoin(Leader, leader_join_cond)\
     .group_by(models.Community.id_community, Leader.id)

    if leader_id:
        query = query.filter(models.Community.leader_id == leader_id)

    results = query.all()
    
    final = []
    for comm, count, l_name, l_email in results:
        comm.member_count = count
        # Fallback logic: prefer name_user, use email if name is empty/null
        comm.leader_name = l_name if l_name else l_email
        final.append(comm)
        
    return final

def get_by_id(db: Session, community_id: int):
    Member = aliased(User)
    Leader = aliased(User)
    
    # Same flexible join condition
    leader_join_cond = or_(
        models.Community.leader_id == Leader.id,
        and_(Leader.rol_id == 3, Leader.community_id == models.Community.id_community)
    )

    result = db.query(
        models.Community,
        func.count(Member.id).label("member_count"),
        Leader.name_user.label("leader_name_direct"),
        Leader.email.label("leader_email")
    ).outerjoin(Member, Member.community_id == models.Community.id_community)\
     .outerjoin(Leader, leader_join_cond)\
     .filter(models.Community.id_community == community_id)\
     .group_by(models.Community.id_community, Leader.id)\
     .first()

    if result:
        comm, count, l_name, l_email = result
        comm.member_count = count or 0
        comm.leader_name = l_name if l_name else l_email
        return comm
    return None

def create(db: Session, community: schemas.CommunityCreate):
    db_community = models.Community(**community.model_dump())
    db.add(db_community)
    db.commit()
    db.refresh(db_community)
    return get_by_id(db, db_community.id_community)

def update(db: Session, community_id: int, data: dict):
    print(f"Updating community {community_id} with data: {data}")
    db.query(models.Community).filter(models.Community.id_community == community_id).update(data)
    db.commit()
    return get_by_id(db, community_id)

def delete(db: Session, community_id: int):
    community = get_by_id(db, community_id)
    if community:
        db.delete(community)
        db.commit()
    return community
    