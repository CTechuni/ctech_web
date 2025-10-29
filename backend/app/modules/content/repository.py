from sqlalchemy.orm import Session
from app.modules.content import models, schemas

def get_all_contents(db: Session):
    return db.query(models.EducationalContent).all()

def get_content_by_id(db: Session, content_id: int):
    return db.query(models.EducationalContent).filter(models.EducationalContent.id_content == content_id).first()

def create_content(db: Session, content: schemas.EducationalContentCreate):
    db_content = models.EducationalContent(**content.dict())
    db.add(db_content)
    db.commit()
    db.refresh(db_content)
    return db_content

def update_content(db: Session, content_id: int, updated: schemas.EducationalContentUpdate):
    db_content = get_content_by_id(db, content_id)
    if not db_content:
        return None
    for key, value in updated.dict(exclude_unset=True).items():
        setattr(db_content, key, value)
    db.commit()
    db.refresh(db_content)
    return db_content

def delete_content(db: Session, content_id: int):
    db_content = get_content_by_id(db, content_id)
    if not db_content:
        return None
    db.delete(db_content)
    db.commit()
    return db_content
