import os
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:16281826@127.0.0.1:5432/db_CTech"

def check_users_roles():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        print("--- AUDITORÍA DE USUARIOS Y ROLES ---")
        query = text("""
            SELECT id, email, name_user, rol_id, community_id 
            FROM users 
            WHERE email = 'ctech.uni@gmail.com'
        """)
        row = conn.execute(query).fetchone()
        if row:
            print(f"Admin User: {row.email} | Rol ID: {row.rol_id} | Community ID: {row.community_id}")
        else:
            print("Admin user 'ctech.uni@gmail.com' not found.")

if __name__ == "__main__":
    try:
        check_users_roles()
    except Exception as e:
        print(f"Error: {e}")
