"""
Itinerary data models.

Defines the Pydantic response models for the trip planning endpoint.
These models validate and serialize the structured itinerary output
from Gemini into a type-safe API response with full stop details.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class TravelToNext(BaseModel):
    """Transit information between consecutive itinerary stops.

    Attributes:
        duration: Estimated travel time (e.g. '15 min').
        mode: Mode of transport (e.g. 'Walk', 'Metro', 'Taxi').
    """
    duration: str = Field(..., description="Estimated travel time")
    mode: str = Field(..., description="Mode of transport")


class Stop(BaseModel):
    """A single stop in the day's itinerary with full detail.

    Contains venue information, accessibility flags, cost data,
    and a rainy day alternative for outdoor activities.

    Attributes:
        time: Scheduled arrival time (e.g. '10:00').
        name: Venue or place name.
        description: Brief description of the activity or experience.
        neighborhood: Neighborhood or district within the city.
        wheelchair: Whether the venue is wheelchair accessible.
        vegetarian: Whether vegetarian/vegan options are available.
        stepFree: Whether the venue has step-free access.
        cost: Formatted cost string (e.g. '€15', 'Free').
        priceLevel: Price level from 0 (free) to 4 (very expensive).
        streetViewUrl: Google Street View URL for the venue.
        travelToNext: Transit info to the next stop, if applicable.
        rainy_day_fallback: Indoor alternative if it rains.
    """
    time: str = Field(..., description="Scheduled arrival time")
    name: str = Field(..., description="Venue or place name")
    description: str = Field(..., description="Activity description")
    neighborhood: str = Field(default="", description="Neighborhood or district")
    wheelchair: bool = Field(default=False, description="Wheelchair accessible")
    vegetarian: bool = Field(default=False, description="Vegetarian options available")
    stepFree: bool = Field(default=False, description="Step-free access")
    cost: str = Field(..., description="Formatted cost string")
    priceLevel: int = Field(..., ge=0, le=4, description="Price level 0-4")
    streetViewUrl: str = Field(..., description="Google Street View URL")
    travelToNext: Optional[TravelToNext] = Field(default=None, description="Transit to next stop")
    rainy_day_fallback: str = Field(default="", description="Indoor alternative")


class DayPlan(BaseModel):
    """A single day's itinerary plan with ordered stops and total cost.

    Attributes:
        stops: Ordered list of stops for the day.
        totalCost: Formatted total cost for the day (e.g. '€120').
    """
    stops: List[Stop] = Field(..., description="Ordered stops for the day")
    totalCost: str = Field(..., description="Formatted daily total cost")


class Itinerary(BaseModel):
    """Complete multi-day travel itinerary with conflict resolution.

    The top-level response model for the /api/plan endpoint, containing
    the full day-by-day plan, constraint resolution log, and accessibility notes.

    Attributes:
        days: List of day plans, each containing ordered stops.
        conflicts_resolved: Log of how vibe vs constraint conflicts were resolved.
        total_estimated_cost: Total trip cost as a float.
        accessibility_notes: Accessibility guidance for the entire trip.
    """
    days: List[DayPlan] = Field(..., description="Day-by-day itinerary plans")
    conflicts_resolved: List[str] = Field(..., description="Conflict resolution log")
    total_estimated_cost: float = Field(..., description="Total estimated cost")
    accessibility_notes: str = Field(..., description="Trip accessibility guidance")
