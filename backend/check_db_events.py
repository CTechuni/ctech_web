from app.core.database import SessionLocal
from app.modules.events.models import Event
from sqlalchemy import text

def check_events():
    db = SessionLocal()
    try:
        events = db.query(Event).all()
        print(f"Total eventos encontrados: {len(events)}")
        print("-" * 50)
        for e in events:
            print(f"ID: {e.id}")
            print(f"  Title: {e.title}")
            print(f"  Status: {e.status}")
            print(f"  Visibility: {e.visibility}")
            print(f"  Image: {e.image_url}")
            print(f"  Creator: {e.creator_id}")
            print(f"  Community: {e.community_id}")
            print("-" * 50)
    finally:
        db.close()

if __name__ == "__main__":
    check_events()
