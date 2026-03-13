from pydantic import BaseModel
from typing import Dict

class AdminStats(BaseModel):
    total_users: int
    total_communities: int
    active_events: int
    role_distribution: Dict[str, int]
    community_distribution: Dict[str, int]
