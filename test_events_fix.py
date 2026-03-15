import sys
import os

# Añadir el directorio raíz al path para que las importaciones funcionen
sys.path.append(os.path.abspath(os.curdir))
# También añadir el directorio backend si es necesario
sys.path.append(os.path.abspath(os.path.join(os.curdir, "backend")))

from backend.app.core.database import SessionLocal
from backend.app.modules.events import repository, service

def test():
    db = SessionLocal()
    try:
        print("Probando repository.get_all...")
        results = repository.get_all(db, limit=5)
        print(f"Número de resultados: {len(results)}")
        if results:
            first = results[0]
            print(f"Tipo del primer resultado: {type(first)}")
            print(f"Longitud de la tupla: {len(first)}")
            print(f"Valores: {first}")
            
        print("\nProbando service.list_all...")
        events = service.list_all(db, limit=5)
        print(f"Número de eventos procesados: {len(events)}")
        if events:
            print(f"Primer evento community_name: {events[0].community_name}")
            print(f"Primer evento leader_name: {events[0].leader_name}")
            
    except Exception as e:
        print(f"\nERROR detectado: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test()
