import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('backend/.env')
db_url = os.getenv('DATABASE_URL')

if not db_url:
    print("Error: DATABASE_URL no encontrada en backend/.env")
    sys.exit(1)

engine = create_engine(db_url)

with engine.connect() as conn:
    print("--- Líderes actuales (Rol 3) ---")
    leaders = conn.execute(text("SELECT id, name_user, email, community_id FROM users WHERE rol_id = 3")).fetchall()
    for l in leaders:
        print(f"ID: {l.id} | Name: {l.name_user} | Comm ID: {l.community_id}")

    print("\n--- Usuarios con Rol 4 (Posibles ex-líderes degradados) ---")
    # Buscamos nombres conocidos o usuarios recientes sin comunidad
    users = conn.execute(text("SELECT id, name_user, email, community_id FROM users WHERE rol_id = 4 ORDER BY id DESC LIMIT 10")).fetchall()
    for u in users:
        print(f"ID: {u.id} | Name: {u.name_user} | Comm ID: {u.community_id}")

    print("\n--- Comunidades sin líder asignado en la tabla communities ---")
    comms = conn.execute(text("SELECT id_community, name_community, leader_id FROM communities WHERE leader_id IS NULL")).fetchall()
    for c in comms:
        print(f"ID: {c.id_community} | Name: {c.name_community}")
