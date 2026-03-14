import sys
import os

# Add current directory to sys.path
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.modules.users.models import User
from app.modules.communities.models import Community
from app.modules.auth.service import get_password_hash

def fix_hashes():
    db = SessionLocal()
    try:
        # Find the specific user causing the issue
        target_email = "admin@tech.com"
        user = db.query(User).filter(User.email == target_email).first()
        
        if user:
            print(f"Found user: {user.email}")
            print(f"Current hash: {user.password_hash}")
            
            # Reset to a known valid bcrypt hash
            new_password = "Leader123!"
            user.password_hash = get_password_hash(new_password)
            db.commit()
            
            print(f"Successfully reset password for {target_email} to '{new_password}'")
            print(f"New hash: {user.password_hash}")
        else:
            print(f"User {target_email} not found.")

        # Check for any other potentially invalid hashes (not starting with $2b$ or $2a$)
        other_users = db.query(User).filter(User.email != target_email).all()
        for u in other_users:
            if not (u.password_hash.startswith("$2b$") or u.password_hash.startswith("$2a$")):
                print(f"Warning: User {u.email} has potentially invalid hash: {u.password_hash[:10]}...")
                
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_hashes()
