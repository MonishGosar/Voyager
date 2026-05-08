from pydantic import BaseModel
from typing import List

class VibeProfile(BaseModel):
    tags: List[str]
    suggested_destinations: List[dict]
