from sqlalchemy.orm import Session
from app.modules.users.models import Role, User
from app.core.security import get_password_hash
from app.core.config import get_settings
from app.core.logger import get_logger
import logging

logger = get_logger("ctech_api.database")
settings = get_settings()


def seed_data(db: Session):
    """
    Seed initial database data.
    
    This function should only be called once during database initialization.
    It creates default roles and an admin user if they don't exist.
    
    Args:
        db: Database session
        
    Raises:
        Exception: If seeding fails (will be caught and logged)
    """
    try:
        # Seed Roles
        if not db.query(Role).first():
            roles = [
                Role(name_rol="admin", description="Administrador del sistema"),
                Role(name_rol="leader", description="Líder de comunidad"),
                Role(name_rol="user", description="Usuario regular")
            ]
            db.add_all(roles)
            db.commit()
            logger.info("✅ Roles seeded successfully")
        else:
            logger.debug("Roles already exist, skipping")

        # Seed Admin User
        admin_role = db.query(Role).filter_by(name_rol="admin").first()
        
        if admin_role:
            existing_admin = db.query(User).filter_by(email=settings.ADMIN_EMAIL).first()
            
            if not existing_admin:
                try:
                    admin_user = User(
                        name_user="Admin Principal",
                        email=settings.ADMIN_EMAIL,
                        password_hash=get_password_hash(settings.ADMIN_PASSWORD),
                        rol_id=admin_role.id_rol,
                        status="active",
                        is_email_verified=True
                    )
                    db.add(admin_user)
                    db.commit()
                    logger.info(f"✅ Admin user seeded successfully: {settings.ADMIN_EMAIL}")
                except ValueError as e:
                    db.rollback()
                    logger.error(f"❌ Error creating admin user: {str(e)}")
                    raise
            else:
                logger.debug(f"Admin user already exists: {settings.ADMIN_EMAIL}")
        else:
            logger.error("❌ Admin role not found while seeding admin user")
            
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error during database seeding: {str(e)}")
        raise
