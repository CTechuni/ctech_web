from sqlalchemy.orm import Session
from app.modules.users.models import User
from app.modules.courses.models import Course
from app.modules.communities.models import Community
from app.modules.events.models import Event

def get_counts(db: Session):
    return {
        "total_users": db.query(User).count(),
        "total_courses": db.query(Course).count(),
        "total_communities": db.query(Community).count(),
        "active_events": db.query(Event).count()
    }
