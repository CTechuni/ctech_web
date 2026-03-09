
import os
import sys

# Add the current directory to sys.path
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.modules.users.models import User, Role
from app.core.config import get_settings

settings = get_settings()
db = SessionLocal()

admin = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
if admin:
    print(f"Admin found: {admin.email}")
    print(f"Status: {admin.status}")
    print(f"Role ID: {admin.rol_id}")
    
    role = db.query(Role).filter(Role.id_rol == admin.rol_id).first()
    if role:
        print(f"Role Name: {role.name_rol}")
    else:
        print("Role not found!")
else:
    print(f"Admin NOT found for email: {settings.ADMIN_EMAIL}")

db.close()
