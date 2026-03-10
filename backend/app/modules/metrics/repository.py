from sqlalchemy.orm import Session
from sqlalchemy import func
from app.modules.users.models import User, Role
from app.modules.courses.models import Course
from app.modules.communities.models import Community
from app.modules.events.models import Event

def get_counts(db: Session):
    # Conteos básicos
    # Cambiamos para contar todos los usuarios en el sistema para el admin
    total_users = db.query(User).count()
    total_courses = db.query(Course).count()
    total_communities = db.query(Community).filter(Community.status_community == 'Activo').count()
    active_events = db.query(Event).count()

    print(f"[Metrics] Admin Dashboard - Users: {total_users}, Courses: {total_courses}, Communities: {total_communities}, Events: {active_events}")

    # Distribución de roles (Excluyendo Admin por solicitud)
    role_dist = db.query(Role.name_rol, func.count(User.id))\
        .join(User, User.rol_id == Role.id_rol)\
        .filter(Role.name_rol != 'admin')\
        .group_by(Role.name_rol).all()
    role_distribution = {name: count for name, count in role_dist}

    # Miembros por comunidad (usar outerjoin para incluir las que tienen 0 miembros)
    comm_dist = db.query(Community.name_community, func.count(User.id))\
        .outerjoin(User, User.community_id == Community.id_community)\
        .group_by(Community.name_community).all()
    community_distribution = {name: count for name, count in comm_dist}

    # Total absoluto para la gráfica (redundante ahora pero lo mantenemos por consistencia)
    absolute_total_users = total_users
    
    # Historial de crecimiento (7 meses): 6 ceros y el actual
    user_growth = [0, 0, 0, 0, 0, 0, absolute_total_users]

    return {
        "total_users": total_users,
        "total_courses": total_courses,
        "total_communities": total_communities,
        "active_events": active_events,
        "role_distribution": role_distribution,
        "community_distribution": community_distribution,
        "user_growth": user_growth
    }
def get_mentor_counts(db: Session, mentor_id: int, community_id: int):
    from app.modules.courses.models import Course
    courses = db.query(Course).filter(Course.mentor_id == mentor_id).all()
    total_courses = len(courses)
    total_modules = sum(len(c.modules or []) for c in courses)
    active_students = db.query(User).filter(
        User.rol_id == 4,
        User.community_id == community_id
    ).count()
    return {
        "total_courses": total_courses,
        "total_modules": total_modules,
        "active_students": active_students,
    }

def get_community_counts(db: Session, community_id: int):
    # Conteos filtrados por comunidad
    total_users = db.query(User).filter(User.rol_id == 4, User.community_id == community_id).count()
    total_courses = db.query(Course).filter(Course.community_id == community_id).count()
    active_events = db.query(Event).filter(Event.community_id == community_id).count()
    total_mentors = db.query(User).filter(User.rol_id == 2, User.community_id == community_id).count()

    return {
        "total_users": total_users,
        "total_courses": total_courses,
        "active_events": active_events,
        "total_mentors": total_mentors
    }
