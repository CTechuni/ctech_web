from sqlalchemy import text
from app.core.database import engine

def force_fix():
    print("Forcing schema update...")
    with engine.connect() as conn:
        try:
            # Drop constraint if exists to avoid errors on retry
            try:
                conn.execute(text("ALTER TABLE users DROP CONSTRAINT IF EXISTS fk_users_specialty"))
                print("Old constraint dropped (if existed).")
            except:
                pass
                
            # Add column if not exists
            print("Running ALTER TABLE...")
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS specialty_id INTEGER"))
            conn.commit()
            print("Column checked/added.")
            
            # Add foreign key
            print("Adding FK constraint...")
            conn.execute(text("ALTER TABLE users ADD CONSTRAINT fk_users_specialty FOREIGN KEY (specialty_id) REFERENCES specialties(id)"))
            conn.commit()
            print("Constraint added.")
            
            # Verify one last time
            res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='users' AND column_name='specialty_id'"))
            if res.fetchone():
                print("VERIFIED: specialty_id exists in users table.")
            else:
                print("CRITICAL: Failed to add column.")
        except Exception as e:
            print(f"Error during force fix: {e}")

if __name__ == "__main__":
    force_fix()
