"""
Planning constraints data models.

Defines the Pydantic request model for the trip planning endpoint.
This model validates all user-provided constraints including destination,
dates, budget, group configuration, accessibility needs, and the optional
vibe profile from the mood board analysis step.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any


class PlanningConstraints(BaseModel):
    """User-provided constraints for itinerary generation.

    These are the hard limits that the AI must respect when building
    the itinerary. Budget and accessibility always take priority over
    vibe preferences when conflicts arise.

    Attributes:
        destination: Target city or region (e.g. 'Lisbon, Portugal').
        startDate: Trip start date in YYYY-MM-DD format.
        endDate: Trip end date in YYYY-MM-DD format.
        groupType: Group type (solo, couple, friends, family).
        groupSize: Number of travelers.
        currency: Budget currency code (USD, EUR, INR, GBP).
        budget: Total trip budget in the specified currency.
        pace: Travel pace on a 1-3 scale (1=relaxed, 2=balanced, 3=packed).
        accessibility: Dict of accessibility requirements (e.g. wheelchair, vegetarian).
        must_include: Specific venues or experiences to include.
        exclude: Venues or categories to exclude.
        vibe: Optional VibeProfile dict forwarded from the mood board analysis step.
    """
    destination: str = Field(..., description="Target city or region")
    startDate: str = Field(..., description="Trip start date (YYYY-MM-DD)")
    endDate: str = Field(..., description="Trip end date (YYYY-MM-DD)")
    groupType: str = Field(..., description="Group type: solo, couple, friends, family")
    groupSize: int = Field(..., ge=1, le=20, description="Number of travelers")
    currency: str = Field(..., description="Budget currency code")
    budget: float = Field(..., ge=0, description="Total trip budget")
    pace: int = Field(default=2, ge=1, le=3, description="Travel pace 1-3")
    accessibility: Dict[str, bool] = Field(default={}, description="Accessibility requirements")
    must_include: List[str] = Field(default=[], description="Must-include venues")
    exclude: List[str] = Field(default=[], description="Venues to exclude")
    # Vibe profile forwarded from step 1
    origin_city: str = Field(default="", description="City the traveler is departing from")
    vibe: Optional[Dict[str, Any]] = Field(default=None, description="Vibe profile from mood board")
