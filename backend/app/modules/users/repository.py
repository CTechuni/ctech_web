from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, outerjoin
from . import models
from app.modules.communities.models import Community
from app.modules.specialties.models import Specialty

def get_all(db: Session):
    return db.query(models.User).options(joinedload(models.User.profile)).all()

def get_paginated(db: Session, page: int, limit: int, role_id: int = None, search: str = None):
    offset = (page - 1) * limit
    query = db.query(
        models.User,
        Community.name_community,
        Specialty.name.label('spec_name')
    ).options(joinedload(models.User.profile))\
     .outerjoin(Community, models.User.community_id == Community.id_community)\
     .outerjoin(Specialty, models.User.specialty_id == Specialty.id)
    
    if role_id:
        query = query.filter(models.User.rol_id == role_id)
        
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (models.User.name_user.ilike(search_filter)) |
            (models.User.email.ilike(search_filter)) |
            (Community.name_community.ilike(search_filter))
        )
        
    results = query.offset(offset).limit(limit).all()
    
    users = []
    for user, comm_name, spec_name in results:
        user.community_name = comm_name
        user.specialty_name = spec_name
        users.append(user)
    return users

def get_count(db: Session, role_id: int = None, search: str = None):
    query = db.query(func.count(models.User.id))
    if role_id:
        query = query.filter(models.User.rol_id == role_id)
    if search:
        search_filter = f"%{search}%"
        # Need to join with community if we search by community name in count too
        query = query.outerjoin(Community, models.User.community_id == Community.id_community)\
                     .filter(
                        (models.User.name_user.ilike(search_filter)) |
                        (models.User.email.ilike(search_filter)) |
                        (Community.name_community.ilike(search_filter))
                     )
    return query.scalar()

def get_by_id(db: Session, user_id: int):
    return db.query(models.User).options(joinedload(models.User.profile)).filter(models.User.id == user_id).first()

def get_by_role(db: Session, role_id: int):
    return db.query(models.User).options(joinedload(models.User.profile)).filter(models.User.rol_id == role_id).all()

def get_leaders_enriched(db: Session):
    """Returns leaders with community_name, community_code and member_count."""
    # Subquery: count members per community
    MemberCount = db.query(
        models.User.community_id,
        func.count(models.User.id).label('member_count')
    ).filter(models.User.community_id != None).group_by(models.User.community_id).subquery()

    results = db.query(
        models.User,
        Community.name_community,
        Community.code.label('community_code'),
        Community.status_community,
        MemberCount.c.member_count,
        Specialty.name.label('spec_name')
    ).options(joinedload(models.User.profile))\
     .outerjoin(Community, models.User.community_id == Community.id_community)\
     .outerjoin(MemberCount, models.User.community_id == MemberCount.c.community_id)\
     .outerjoin(Specialty, models.User.specialty_id == Specialty.id)\
     .filter(models.User.rol_id == 3)\
     .all()

    leaders = []
    for user, comm_name, comm_code, comm_status, member_count, spec_name in results:
        user.community_name = comm_name
        user.community_code = comm_code
        user.community_status = comm_status
        user.member_count = member_count or 0
        user.specialty_name = spec_name
        leaders.append(user)
    return leaders

def get_mentors_enriched(db: Session):
    """Returns mentors with community_name and specialty_name."""
    results = db.query(
        models.User,
        Community.name_community,
        Specialty.name.label('spec_name')
    ).options(joinedload(models.User.profile))\
     .outerjoin(Community, models.User.community_id == Community.id_community)\
     .outerjoin(Specialty, models.User.specialty_id == Specialty.id)\
     .filter(models.User.rol_id == 2)\
     .all()

    mentors = []
    for user, comm_name, spec_name in results:
        user.community_name = comm_name
        user.specialty_name = spec_name
        mentors.append(user)
    return mentors

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
