from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, date

class ModuleItem(BaseModel):
    title: str
    description: Optional[str] = None
    type: str = "link"   # pdf | image | book | video | link
    url: Optional[str] = None

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
    level: str = "basico"          # basico | intermedio | avanzado
    start_date: Optional[date] = None
    modules: List[ModuleItem] = []

class CourseCreate(CourseBase):
    # "draft" = borrador (no notifica al líder)
    # "pending" = publicado (enviado a revisión del líder)
    status: str = "pending"

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_premium: Optional[bool] = None
    technologies: Optional[List[str]] = None
    content_links: Optional[Dict[str, List[str]]] = None
    thumbnail_url: Optional[str] = None
    specialty_id: Optional[int] = None
    level: Optional[str] = None
    start_date: Optional[date] = None
    modules: Optional[List[ModuleItem]] = None
    status: Optional[str] = None   # permite pasar de "draft" a "pending"

class CourseResponse(CourseBase):
    id: int
    status: str = "pending"
    created_at: datetime
    mentor_name: Optional[str] = None
    specialty_name: Optional[str] = None
    enrolled_count: Optional[int] = None

    class Config:
        from_attributes = True
