"""
Trip planning router — generates AI-powered itineraries.

Accepts planning constraints (destination, dates, budget, accessibility)
along with an optional vibe profile, and generates a day-by-day itinerary
using Gemini with conflict resolution and geographic clustering.

Endpoints:
    POST /api/plan — Submit constraints, receive a full Itinerary
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Any
import logging

from models.constraints import PlanningConstraints
from models.itinerary import Itinerary
from services.gemini_service import generate_itinerary

logger = logging.getLogger(__name__)

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

    Raises:
        HTTPException(422): If constraints fail validation.
        HTTPException(500): If Gemini itinerary generation fails.
    """
    try:
        data: dict[str, Any] = constraints.model_dump()
        vibe: dict[str, Any] = data.pop("vibe", None) or {}
        res: dict[str, Any] = generate_itinerary(data, vibe)
        return Itinerary(**res)
    except ValueError as e:
        logger.error(
            "plan_trip: validation error for destination=%s: %s",
            constraints.destination,
            e,
        )
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(
            "plan_trip: failed to generate itinerary for destination=%s: %s",
            constraints.destination,
            e,
        )
        raise HTTPException(
            status_code=500,
            detail="Itinerary generation failed. Please try again.",
        )
