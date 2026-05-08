from pydantic import BaseModel
from typing import List, Optional

class Stop(BaseModel):
    time: str
    name: str
    description: str
    wheelchair: bool = False
    vegetarian: bool = False
    stepFree: bool = False
    cost: str
    priceLevel: int
    streetViewUrl: str
    travelToNext: Optional[dict] = None

class DayPlan(BaseModel):
    stops: List[Stop]
    totalCost: str

class Itinerary(BaseModel):
    days: List[DayPlan]
    conflicts_resolved: List[str]
    total_estimated_cost: float
    accessibility_notes: str
