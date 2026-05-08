from fastapi import APIRouter
from backend.models.constraints import PlanningConstraints
from backend.models.itinerary import Itinerary
from backend.services.gemini_service import generate_itinerary

router = APIRouter()

@router.post("/plan", response_model=Itinerary)
async def plan_trip(constraints: PlanningConstraints):
    res = generate_itinerary(constraints.model_dump())
    return Itinerary(**res)
