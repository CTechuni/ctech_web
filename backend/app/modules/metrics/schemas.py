from pydantic import BaseModel

class AdminStats(BaseModel):
    total_users: int
    total_courses: int
    total_communities: int
    active_events: int
