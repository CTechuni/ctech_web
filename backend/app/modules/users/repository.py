from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, outerjoin
from . import models
from app.modules.communities.models import Community

def get_all(db: Session):
    return db.query(models.User).options(joinedload(models.User.profile)).all()

def get_paginated(db: Session, page: int, limit: int, role_id: int = None, search: str = None):
    offset = (page - 1) * limit
    query = db.query(
        models.User,
        Community.name_community
    ).options(joinedload(models.User.profile))\
     .outerjoin(Community, models.User.community_id == Community.id_community)
    
    if role_id:
        query = query.filter(models.User.rol_id == role_id)
        
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (models.User.name_user.ilike(search_filter)) |
            (models.User.email.ilike(search_filter)) |
            (Community.name_community.ilike(search_filter))
        )
        
    query = query.order_by(models.User.created_at.desc())
    results = query.offset(offset).limit(limit).all()
    
    users = []
    for user, comm_name in results:
        user.community_name = comm_name
        users.append(user)
    return users

def get_count(db: Session, role_id: int = None, search: str = None):
    query = db.query(func.count(models.User.id))
    if role_id:
        query = query.filter(models.User.rol_id == role_id)
    if search:
        search_filter = f"%{search}%"
        query = query.outerjoin(Community, models.User.community_id == Community.id_community)\
                     .filter(
                        (models.User.name_user.ilike(search_filter)) |
                        (models.User.email.ilike(search_filter)) |
                        (Community.name_community.ilike(search_filter))
                     )
    return query.scalar()

def get_by_id(db: Session, user_id: int):
    result = db.query(
        models.User,
        Community.name_community
    ).options(joinedload(models.User.profile))\
     .outerjoin(Community, models.User.community_id == Community.id_community)\
     .filter(models.User.id == user_id).first()

    if result is None:
        return None
    user, comm_name = result
    user.community_name = comm_name
    return user

def get_by_role(db: Session, role_id: int):
    return db.query(models.User).options(joinedload(models.User.profile)).filter(models.User.rol_id == role_id).all()

def get_leaders_enriched(db: Session, only_available: bool = False):
    """Returns leaders with community_name, community_code and member_count."""
    # Subquery: count members per community
    MemberCount = db.query(
        models.User.community_id,
        func.count(models.User.id).label('member_count')
    ).filter(models.User.community_id != None).group_by(models.User.community_id).subquery()

    # Base query centered on User
    query = db.query(models.User).options(joinedload(models.User.profile)).filter(models.User.rol_id == 3)

    # Join with Community and MemberCount
    query = query.outerjoin(Community, models.User.community_id == Community.id_community)\
                 .outerjoin(MemberCount, models.User.community_id == MemberCount.c.community_id)

    # Add columns from joined tables
    query = query.add_columns(
        Community.name_community,
        Community.code.label('community_code'),
        Community.status_community,
        MemberCount.c.member_count
    )

    if only_available:
        query = query.filter(models.User.community_id == None)

    results = query.order_by(models.User.created_at.desc()).all()

    leaders = []
    # results is a list of tuples: (User, name, code, status, count)
    for row in results:
        user = row[0]
        user.community_name = row[1]
        user.community_code = row[2]
        user.community_status = row[3]
        user.member_count = row[4] or 0
        leaders.append(user)
    return leaders

def update(db: Session, user_id: int, data: dict):
    db.query(models.User).filter(models.User.id == user_id).update(data)
    db.commit()
    return get_by_id(db, user_id)

def delete(db: Session, user_id: int):
    user = get_by_id(db, user_id)
    if user:
        db.delete(user)
        db.commit()
    return user

def get_by_community(db: Session, community_id: int):
    return db.query(models.User).options(joinedload(models.User.profile)).filter(models.User.community_id == community_id).all()

def create(db: Session, user_data: dict):
    db_user = models.User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
