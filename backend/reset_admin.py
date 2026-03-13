import sys
import os

# Añadir el path actual al sys.path para que pueda importar 'app'
sys.path.append(os.getcwd())

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.modules.users.models import User, Role
from app.modules.auth.service import get_password_hash
from app.core.config import get_settings

def reset_admin():
    settings = get_settings()
    db = SessionLocal()
    
    email = settings.ADMIN_EMAIL
    password = settings.ADMIN_PASSWORD
    
    print(f"Checking for admin: {email}")
    
    try:
        admin_user = db.query(User).filter(User.email == email).first()
        
        if admin_user:
            print(f"Admin found. Resetting password to: {password}")
            admin_user.password_hash = get_password_hash(password)
            db.commit()
            print("Password reset successful.")
        else:
            print("Admin NOT found. Creating...")
            # Ensure admin role exists
            admin_role = db.query(Role).filter(Role.name_rol == "admin").first()
            if not admin_role:
                print("Admin role missing. Creating role...")
                admin_role = Role(name_rol="admin", description="Administrador")
                db.add(admin_role)
                db.commit()
                db.refresh(admin_role)
            
            new_admin = User(
                email=email,
                password_hash=get_password_hash(password),
                name_user="Admin Principal",
                rol_id=admin_role.id_rol,
                status="active",
                is_email_verified=True
            )
            db.add(new_admin)
            db.commit()
            print("Admin created successfully.")
            
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_admin()
