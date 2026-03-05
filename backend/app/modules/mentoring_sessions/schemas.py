from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SessionBase(BaseModel):
    course_id: int
    scheduled_at: datetime
    meeting_link: Optional[str] = None

class SessionCreate(SessionBase):
    pass # El mentor_id se asignará automáticamente desde el token

class SessionResponse(SessionBase):
    id: int
    mentor_id: int
    student_id: Optional[int] = None
    status: str

    class Config:
        from_attributes = True
