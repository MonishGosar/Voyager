from pydantic import BaseModel
from typing import List, Dict

class PlanningConstraints(BaseModel):
    destination: str
    startDate: str
    endDate: str
    groupType: str
    groupSize: int
    currency: str
    budget: float
    pace: int
    accessibility: Dict[str, bool]
