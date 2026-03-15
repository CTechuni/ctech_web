from datetime import date as date_type
from sqlalchemy.orm import Session, aliased
from sqlalchemy import func, or_
from . import models, schemas
from app.modules.communities.models import Community
from app.modules.users.models import User

# Alias para el líder de la comunidad del evento
Leader = aliased(User)

def _with_community(query):
    return query.outerjoin(Community, models.Event.community_id == Community.id_community)\
                .outerjoin(Leader, Community.leader_id == Leader.id)

def _base_query(db: Session):
    registered_count = (
        db.query(func.count(models.EventRegistration.id))
        .filter(models.EventRegistration.event_id == models.Event.id)
        .correlate(models.Event)
        .scalar_subquery()
    )
    return db.query(
        models.Event,
        Community.name_community.label("community_name"),
        Leader.name_user.label("leader_name"),
        registered_count.label("registered_count")
    )

def _apply_filters(query, upcoming_only: bool, community_id: int | None, event_type: str | None):
    """Aplica filtros opcionales compartidos entre los listados."""
    if upcoming_only:
        query = query.filter(models.Event.event_date >= date_type.today())
    if community_id is not None:
        query = query.filter(models.Event.community_id == community_id)
    if event_type is not None:
        query = query.filter(models.Event.event_type == event_type)
    return query

def _paginate(query, skip: int, limit: int):
    return query.order_by(models.Event.event_date.asc()).offset(skip).limit(limit).all()

def get_all(db: Session, skip: int = 0, limit: int = 20,
            upcoming_only: bool = False, community_id: int | None = None,
            event_type: str | None = None):
    """Todos los eventos — solo admin."""
    q = _with_community(_base_query(db))
    return _paginate(_apply_filters(q, upcoming_only, community_id, event_type), skip, limit)

def get_approved_public(db: Session, skip: int = 0, limit: int = 20,
                        upcoming_only: bool = True, community_id: int | None = None,
                        event_type: str | None = None):
    """Eventos aprobados y públicos."""
    q = _with_community(_base_query(db)).filter(
        models.Event.status == "approved",
        models.Event.visibility == "publico"
    )
    return _paginate(_apply_filters(q, upcoming_only, community_id, event_type), skip, limit)

def get_approved(db: Session, skip: int = 0, limit: int = 20,
                   upcoming_only: bool = True, community_id: int | None = None,
                   event_type: str | None = None):
    """Eventos aprobados (públicos y privados)."""
    q = _with_community(_base_query(db)).filter(models.Event.status == "approved")
    return _paginate(_apply_filters(q, upcoming_only, community_id, event_type), skip, limit)

def get_approved_for_user(db: Session, user_community_id: int | None, skip: int = 0, limit: int = 20,
                           upcoming_only: bool = True, event_type: str | None = None):
    """
    Eventos que un usuario puede ver:
    - Públicos aprobados
    - Privados aprobados de SU comunidad
    """
    filters = [
        (models.Event.visibility == "publico") & (models.Event.status == "approved")
    ]
    if user_community_id:
        filters.append(
            (models.Event.visibility == "privado") & 
            (models.Event.community_id == user_community_id) & 
            (models.Event.status == "approved")
        )
    
    q = _with_community(_base_query(db)).filter(or_(*filters))
    return _paginate(_apply_filters(q, upcoming_only, None, event_type), skip, limit)

def get_pending_by_community(db: Session, community_id: int):
    """Eventos pendientes de aprobación de una comunidad."""
    return _with_community(_base_query(db)).filter(
        models.Event.status == "pending",
        models.Event.community_id == community_id
    ).order_by(models.Event.event_date.asc()).all()

def get_all_pending(db: Session):
    """Todos los eventos pendientes de aprobación (solo admin)."""
    return _with_community(_base_query(db)).filter(
        models.Event.status == "pending"
    ).order_by(models.Event.event_date.asc()).all()

def get_by_community(db: Session, community_id: int, skip: int = 0, limit: int = 20,
                     upcoming_only: bool = False, event_type: str | None = None):
    """Eventos de una comunidad específica."""
    q = _with_community(_base_query(db)).filter(models.Event.community_id == community_id)
    return _paginate(_apply_filters(q, upcoming_only, None, event_type), skip, limit)

def get_by_creator(db: Session, creator_id: int, skip: int = 0, limit: int = 20):
    """Eventos creados por un usuario específico."""
    q = _with_community(_base_query(db)).filter(models.Event.creator_id == creator_id)
    return _paginate(q, skip, limit)

def get_upcoming(db: Session, limit: int = 5, public_only: bool = False):
    """Próximos eventos aprobados."""
    q = _with_community(_base_query(db)).filter(
        models.Event.status == "approved",
        models.Event.event_date >= date_type.today()
    )
    if public_only:
        q = q.filter(models.Event.visibility == "publico")
    return q.order_by(models.Event.event_date.asc(), models.Event.event_time.asc()).limit(limit).all()

def get_by_id(db: Session, event_id: int):
    return db.query(models.Event).filter(models.Event.id == event_id).first()

def create(db: Session, data: schemas.EventCreate):
    db_event = models.Event(**data.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def approve(db: Session, event_id: int):
    event = get_by_id(db, event_id)
    if event:
        event.status = "approved"
        db.commit()
        db.refresh(event)
    return event

def reject(db: Session, event_id: int):
    event = get_by_id(db, event_id)
    if event:
        event.status = "rejected"
        db.commit()
        db.refresh(event)
    return event

def cancel(db: Session, event_id: int):
    event = get_by_id(db, event_id)
    if event:
        event.status = "cancelled"
        db.commit()
        db.refresh(event)
    return event

def postpone(db: Session, event_id: int):
    event = get_by_id(db, event_id)
    if event:
        event.status = "postponed"
        db.commit()
        db.refresh(event)
    return event

def delete(db: Session, event_id: int):
    event = get_by_id(db, event_id)
    if event:
        db.delete(event)
        db.commit()
        return True
    return False

# ── Registros de asistencia ───────────────────────────────────────────────────

def get_registration(db: Session, event_id: int, user_id: int):
    return db.query(models.EventRegistration).filter(
        models.EventRegistration.event_id == event_id,
        models.EventRegistration.user_id == user_id
    ).first()

def create_registration(db: Session, event_id: int, user_id: int):
    reg = models.EventRegistration(event_id=event_id, user_id=user_id)
    db.add(reg)
    db.commit()
    db.refresh(reg)
    return reg

def delete_registration(db: Session, event_id: int, user_id: int):
    reg = get_registration(db, event_id, user_id)
    if reg:
        db.delete(reg)
        db.commit()
        return True
    return False

def count_registrations(db: Session, event_id: int):
    return db.query(func.count(models.EventRegistration.id)).filter(
        models.EventRegistration.event_id == event_id
    ).scalar()

def get_registrations_by_event(db: Session, event_id: int):
    from app.modules.users.models import User
    return db.query(User).join(
        models.EventRegistration,
        models.EventRegistration.user_id == User.id
    ).filter(models.EventRegistration.event_id == event_id).all()

def get_registered_event_ids(db: Session, user_id: int):
    rows = db.query(models.EventRegistration.event_id).filter(
        models.EventRegistration.user_id == user_id
    ).all()
    return {r[0] for r in rows}
