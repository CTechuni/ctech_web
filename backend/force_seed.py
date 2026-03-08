from app.core.database import SessionLocal
from app.db.init_db import seed_data
from app.modules.users.models import User

def force_seed():
    print("Forcing seed data execution...")
    db = SessionLocal()
    try:
        # Check if we can query User table first
        admin = db.query(User).filter(User.id == 1).first()
        print(f"Connection test successful. Admin check: {admin.email if admin else 'Not found'}")
        
        seed_data(db)
        print("Success: seed_data executed without errors.")
    except Exception as e:
        print(f"Error during seeding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    force_seed()
