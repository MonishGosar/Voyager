"""
Vibe profile data models.

Defines the Pydantic response models for the vibe analysis endpoint.
These models validate and serialize the structured output from Gemini's
mood board analysis into a type-safe API response.
"""

from pydantic import BaseModel, Field
from typing import List


class PlaceSignal(BaseModel):
    """A signal extracted from a mood board photo about trip intent.

    Attributes:
        type: Category of place (restaurant, landmark, neighborhood, hotel, activity).
        vibe: What this place signals about the traveler's preferences.
    """
    type: str = Field(..., description="Category: restaurant, landmark, neighborhood, hotel, or activity")
    vibe: str = Field(..., description="What this place signals about trip intent")


class Destination(BaseModel):
    """A suggested travel destination inferred from mood board analysis.

    Attributes:
        name: City name (e.g. 'Porto').
        country: Country name (e.g. 'Portugal').
    """
    name: str = Field(..., description="City name")
    country: str = Field(..., description="Country name")


class VibeProfile(BaseModel):
    """Structured vibe profile extracted from mood board photos.

    Contains all signals the AI extracts from uploaded travel inspiration
    images, used to personalize itinerary generation with soft preferences.

    Attributes:
        tags: 4-6 specific, sensory vibe tags (e.g. 'candlelit wine caves').
        mood: One-sentence emotional summary of the desired trip.
        travel_style: Closest travel style archetype.
        pace: Inferred trip pace (relaxed, balanced, packed).
        place_signals: List of place-intent signals from photos.
        must_haves: Inferred non-negotiable trip elements.
        avoid_hints: What's absent from the board (things to avoid).
        suggested_destinations: 3 AI-matched destination cities.
        meal_style: Inferred dining preference.
        time_of_day_preference: Preferred time of day for activities.
    """
    tags: List[str] = Field(..., description="4-6 specific sensory vibe tags")
    mood: str = Field(default="", description="One-sentence emotional trip summary")
    travel_style: str = Field(default="slow explorer", description="Travel style archetype")
    pace: str = Field(default="balanced", description="Trip pace: relaxed, balanced, or packed")
    place_signals: List[PlaceSignal] = Field(default=[], description="Place-intent signals")
    must_haves: List[str] = Field(default=[], description="Non-negotiable trip elements")
    avoid_hints: List[str] = Field(default=[], description="Things to avoid based on absence")
    suggested_destinations: List[Destination] = Field(..., description="3 AI-matched destinations")
    meal_style: str = Field(default="mixed", description="Dining preference")
    time_of_day_preference: str = Field(default="all-day", description="Preferred activity time")
