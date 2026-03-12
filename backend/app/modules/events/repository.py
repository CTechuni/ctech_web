from sqlalchemy.orm import Session
from . import models, schemas
from app.modules.communities.models import Community

def _with_community(query):
    return query.outerjoin(Community, models.Event.community_id == Community.id_community)

def _base_query(db: Session):
    return db.query(models.Event, Community.name_community.label("community_name"))

# ── Consultas de listado ───────────────────────────────────────────────────────

def get_approved_public(db: Session):
    """Eventos aprobados y públicos — para visitantes sin auth."""
    return _with_community(_base_query(db)).filter(
        models.Event.status == "approved",
        models.Event.visibility == "publico"
    ).order_by(models.Event.event_date.asc()).all()

def get_approved(db: Session):
    """Eventos aprobados (cualquier visibilidad) — para usuarios autenticados."""
    return _with_community(_base_query(db)).filter(
        models.Event.status == "approved"
    ).order_by(models.Event.event_date.asc()).all()

def get_all(db: Session):
    """Todos los eventos — solo admin."""
    return _with_community(_base_query(db)).order_by(models.Event.event_date.asc()).all()

def get_by_community(db: Session, community_id: int):
    """Todos los eventos de una comunidad — para el líder."""
    return _with_community(_base_query(db)).filter(
        models.Event.community_id == community_id
    ).order_by(models.Event.event_date.asc()).all()

def get_pending_by_community(db: Session, community_id: int):
    """Eventos pendientes de aprobación de una comunidad."""
    return _with_community(_base_query(db)).filter(
        models.Event.status == "pending",
        models.Event.community_id == community_id
    ).order_by(models.Event.event_date.asc()).all()

def get_all_pending(db: Session):
    """Todos los eventos pendientes — solo admin."""
    return _with_community(_base_query(db)).filter(
        models.Event.status == "pending"
    ).order_by(models.Event.event_date.asc()).all()

# ── CRUD ──────────────────────────────────────────────────────────────────────

def get_by_id(db: Session, event_id: int):
    return db.query(models.Event).filter(models.Event.id == event_id).first()

def create(db: Session, event_data: schemas.EventCreate):
    data = event_data.model_dump()
    db_event = models.Event(**data)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def update(db: Session, event_id: int, data: dict):
    db.query(models.Event).filter(models.Event.id == event_id).update(data)
    db.commit()
    return get_by_id(db, event_id)

def approve(db: Session, event_id: int):
    return update(db, event_id, {"status": "approved"})

def reject(db: Session, event_id: int):
    return update(db, event_id, {"status": "rejected"})

def get_upcoming(db: Session, limit: int = 5, public_only: bool = False):
    from datetime import date
    today = date.today()
    q = _with_community(_base_query(db)).filter(
        models.Event.event_date >= today,
        models.Event.status == "approved"
    )
    if public_only:
        q = q.filter(models.Event.visibility == "publico")
    return q.order_by(models.Event.event_date.asc(), models.Event.event_time.asc()).limit(limit).all()

def update_image(db: Session, event_id: int, url: str):
    db_event = get_by_id(db, event_id)
    if db_event:
        db_event.image_url = url
        db.commit()
    return db_event

def delete(db: Session, event_id: int):
    db_event = get_by_id(db, event_id)
    if db_event:
        db.delete(db_event)
        db.commit()
        return True
    return False

# ── Registros de asistentes ────────────────────────────────────────────────────

def get_registration(db: Session, event_id: int, user_id: int):
    return db.query(models.EventRegistration).filter(
        models.EventRegistration.event_id == event_id,
        models.EventRegistration.user_id == user_id
    ).first()

def count_registrations(db: Session, event_id: int) -> int:
    return db.query(models.EventRegistration).filter(
        models.EventRegistration.event_id == event_id
    ).count()

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

def get_registrations_by_event(db: Session, event_id: int):
    from app.modules.users.models import User
    return db.query(User).join(
        models.EventRegistration,
        models.EventRegistration.user_id == User.id
    ).filter(models.EventRegistration.event_id == event_id).all()
