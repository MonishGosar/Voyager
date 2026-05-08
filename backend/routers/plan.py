"""
Trip planning router — generates AI-powered itineraries.

Accepts planning constraints (destination, dates, budget, accessibility)
along with an optional vibe profile, and generates a day-by-day itinerary
using Gemini with conflict resolution and geographic clustering.

Endpoints:
    POST /api/plan — Submit constraints, receive a full Itinerary
"""

from fastapi import APIRouter
from typing import Any

from models.constraints import PlanningConstraints
from models.itinerary import Itinerary
from services.gemini_service import generate_itinerary

router = APIRouter()


@router.post("/plan", response_model=Itinerary)
async def plan_trip(constraints: PlanningConstraints) -> Itinerary:
    """Generate a vibe-driven, constraint-resolved travel itinerary.

    Takes the user's hard constraints and soft vibe preferences,
    feeds them to Gemini, and returns a fully structured itinerary
    with geographically clustered stops, accessibility badges,
    rainy day alternatives, and cost breakdowns.

    Args:
        constraints: PlanningConstraints with destination, dates, budget,
            group info, accessibility needs, and optional vibe profile.

    Returns:
        Itinerary with days (each containing stops), conflicts_resolved,
        total_estimated_cost, and accessibility_notes.
    """
    data: dict[str, Any] = constraints.model_dump()
    vibe: dict = data.pop("vibe", None) or {}
    res = generate_itinerary(data, vibe)
    return Itinerary(**res)
