from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    is_premium: bool = False
    technologies: List[str] = []
    content_links: Dict[str, List[str]] = {"pdfs": [], "books": [], "videos": []}
    thumbnail_url: Optional[str] = None
    community_id: Optional[int] = None
    mentor_id: Optional[int] = None
    specialty_id: Optional[int] = None

class CourseCreate(CourseBase):
    pass

class CourseUpdate(CourseBase):
    title: Optional[str] = None

class CourseResponse(CourseBase):
    id: int
    created_at: datetime
    mentor_name: Optional[str] = None
    specialty_name: Optional[str] = None

    class Config:
        from_attributes = True
