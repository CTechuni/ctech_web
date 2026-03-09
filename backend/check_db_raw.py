from app.core.database import SessionLocal, engine
from sqlalchemy import text

db = SessionLocal()
try:
    print("--- Roles ---")
    res = db.execute(text("SELECT id_rol, name_rol FROM roles"))
    for row in res:
        print(f"Role ID: {row[0]} | Name: {row[1]}")
        
    print("\n--- User Counts by Role ---")
    res = db.execute(text("SELECT rol_id, COUNT(*) FROM users GROUP BY rol_id"))
    for row in res:
        print(f"Role ID: {row[0]} | Count: {row[1]}")
        
    print("\n--- Community Status Counts ---")
    res = db.execute(text("SELECT status_community, COUNT(*) FROM communities GROUP BY status_community"))
    for row in res:
        print(f"Status: {row[0]} | Count: {row[1]}")

    print("\n--- Other Counts ---")
    res = db.execute(text("SELECT COUNT(*) FROM courses")).scalar()
    print(f"Courses: {res}")
    res = db.execute(text("SELECT COUNT(*) FROM events")).scalar()
    print(f"Events: {res}")

finally:
    db.close()
