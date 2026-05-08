from fastapi import APIRouter
from models.constraints import PlanningConstraints
from models.itinerary import Itinerary
from services.gemini_service import generate_itinerary

router = APIRouter()

@router.post("/plan", response_model=Itinerary)
async def plan_trip(constraints: PlanningConstraints):
    res = generate_itinerary(constraints.model_dump())
    return Itinerary(**res)
