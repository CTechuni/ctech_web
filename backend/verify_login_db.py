
import os
import sys

# Add current directory to path
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.db.base_api import Base, User, Role
from app.core.config import get_settings
from app.modules.auth.service import verify_password

settings = get_settings()
db = SessionLocal()

print(f"Checking for admin: {settings.ADMIN_EMAIL}")
admin = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()

if admin:
    print(f"Admin found: {admin.email}")
    print(f"Status: {admin.status}")
    print(f"Role ID: {admin.rol_id}")
    
    test_pw = settings.ADMIN_PASSWORD
    is_valid = verify_password(test_pw, admin.password_hash)
    print(f"Password verification for '{test_pw}': {is_valid}")
else:
    print("Admin NOT found!")
    users = db.query(User).all()
    print(f"Users in DB: {[u.email for u in users]}")

db.close()
