import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')
db_url = os.getenv('DATABASE_URL')

if not db_url:
    print("Error: DATABASE_URL no encontrada")
    sys.exit(1)

engine = create_engine(db_url)

# Usuarios identificados como lideres afectados
# 18: Jhoan Monsalve (Mencionado por el usuario)
# 19: Eliana Gallego
# 20: Lider Prueba
# 21: Maicol Cordoba
# 24: Jose Daniel
affected_ids = [18, 19, 20, 21, 24]

with engine.connect() as conn:
    print(f"Restaurando rol 3 a los usuarios: {affected_ids}")
    res = conn.execute(text("UPDATE users SET rol_id = 3 WHERE id IN :ids"), {"ids": tuple(affected_ids)})
    conn.commit()
    print(f"Filas actualizadas: {res.rowcount}")

    # Verificar resultado
    print("\nEstado actual de los usuarios afectados:")
    check = conn.execute(text("SELECT id, name_user, rol_id, community_id FROM users WHERE id IN :ids"), {"ids": tuple(affected_ids)}).fetchall()
    for u in check:
        print(f"ID: {u.id} | Name: {u.name_user} | Role: {u.rol_id} | Comm: {u.community_id}")
