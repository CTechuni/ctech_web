from app.core.database import SessionLocal
from app.modules.users.models import User, Role
from app.modules.courses.models import Course
from app.modules.communities.models import Community
from app.modules.events.models import Event

db = SessionLocal()
try:
    print(f"Total Users: {db.query(User).count()}")
    print(f"Total Roles: {db.query(Role).count()}")
    print(f"Total Courses: {db.query(Course).count()}")
    print(f"Total Communities: {db.query(Community).count()}")
    print(f"Total Events: {db.query(Event).count()}")
    
    # Check users by role
    roles = db.query(Role).all()
    for role in roles:
        count = db.query(User).filter(User.rol_id == role.id_rol).count()
        print(f"Users with role '{role.name_rol}' (ID {role.id_rol}): {count}")
    
    # Check community statuses
    comms = db.query(Community).all()
    for comm in comms:
        print(f"Community: {comm.name_community}, Status: {comm.status_community}")

finally:
    db.close()
