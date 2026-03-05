from app.core.database import SessionLocal
from app.modules.specialties.models import Specialty

def seed_data():
    db = SessionLocal()
    # Lista fija de especialidades
    specialties = ["Frontend", "Backend", "Fullstack", "Mobile", "Data Science", "DevOps"]
    
    for name in specialties:
        # Solo lo agrega si no existe ya
        exists = db.query(Specialty).filter(Specialty.name == name).first()
        if not exists:
            new_spec = Specialty(name=name)
            db.add(new_spec)
    
    db.commit()
    db.close()
    print("¡Especialidades cargadas con éxito!")

if __name__ == "__main__":
    seed_data()