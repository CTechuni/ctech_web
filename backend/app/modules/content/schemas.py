from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class EducationalContentBase(BaseModel):
    title: str
    description_content: Optional[str] = None
    url_file: Optional[str] = None
    type_content: str
    area_id: int
    level_id: int
    author_id: int
    status_content: str = "activo"

class EducationalContentCreate(EducationalContentBase):
    pass

class EducationalContentUpdate(EducationalContentBase):
    pass

class EducationalContentResponse(EducationalContentBase):
    id_content: int
    upload_date: datetime

    class Config:
        from_attributes = True
