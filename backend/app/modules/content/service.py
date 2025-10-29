from sqlalchemy.orm import Session
from app.modules.content import repository, schemas

def list_contents(db: Session):
    return repository.get_all_contents(db)

def get_content(db: Session, content_id: int):
    return repository.get_content_by_id(db, content_id)

def create_content(db: Session, content: schemas.EducationalContentCreate):
    return repository.create_content(db, content)

def update_content(db: Session, content_id: int, updated: schemas.EducationalContentUpdate):
    return repository.update_content(db, content_id, updated)

def delete_content(db: Session, content_id: int):
    return repository.delete_content(db, content_id)
