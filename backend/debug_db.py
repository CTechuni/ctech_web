from sqlalchemy import text
from app.core.database import engine

def check_tables():
    print("Checking tables...")
    with engine.connect() as conn:
        try:
            res = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
            tables = [row[0] for row in res.fetchall()]
            print(f"Existing tables: {tables}")
            
            res = conn.execute(text("SELECT column_name, is_nullable FROM information_schema.columns WHERE table_name='users'"))
            columns = {row[0]: row[1] for row in res.fetchall()}
            print(f"Users columns: {columns}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    check_tables()
