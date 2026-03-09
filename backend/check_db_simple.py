from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    print(f"COUNT_USERS_TOTAL={db.execute(text('SELECT COUNT(*) FROM users')).scalar()}")
    print(f"COUNT_USERS_ROLE1={db.execute(text('SELECT COUNT(*) FROM users WHERE rol_id=1')).scalar()}")
    print(f"COUNT_USERS_ROLE2={db.execute(text('SELECT COUNT(*) FROM users WHERE rol_id=2')).scalar()}")
    print(f"COUNT_USERS_ROLE3={db.execute(text('SELECT COUNT(*) FROM users WHERE rol_id=3')).scalar()}")
    print(f"COUNT_USERS_ROLE4={db.execute(text('SELECT COUNT(*) FROM users WHERE rol_id=4')).scalar()}")
    print(f"COUNT_COMMUNITIES_TOTAL={db.execute(text('SELECT COUNT(*) FROM communities')).scalar()}")
    print(f"COUNT_COMMUNITIES_ACTIVE={db.execute(text('SELECT COUNT(*) FROM communities WHERE status_community=\'Activo\'')).scalar()}")
    print(f"COUNT_COURSES={db.execute(text('SELECT COUNT(*) FROM courses')).scalar()}")
    print(f"COUNT_EVENTS={db.execute(text('SELECT COUNT(*) FROM events')).scalar()}")
finally:
    db.close()
