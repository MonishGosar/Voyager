"""
Gemini AI service for travel vibe analysis and itinerary generation.

This module provides the core AI intelligence layer of Voyager, using
Google's Gemini 2.5 Flash model via the google-genai SDK. It handles:

    - Mood board photo analysis → structured VibeProfile extraction
    - Constraint-aware itinerary generation with conflict resolution

All prompts, model names, and configuration are sourced from constants.py
to ensure maintainability. Responses use Gemini's structured output mode
with TypedDict schemas for type safety.
"""

from google import genai
from google.genai import types
from config import settings
from constants import (
    GEMINI_MODEL,
    GEMINI_VIBE_TEMPERATURE,
    GEMINI_ITINERARY_TEMPERATURE,
    GEMINI_RESPONSE_MIME_TYPE,
    VIBE_ANALYSIS_SYSTEM_PROMPT,
    ITINERARY_SYSTEM_PROMPT,
    DEFAULT_DESTINATION,
    DEFAULT_NUM_DAYS,
    DEFAULT_BUDGET,
    DEFAULT_CURRENCY,
    DEFAULT_GROUP_TYPE,
    DEFAULT_GROUP_SIZE,
    DEFAULT_TRAVEL_STYLE,
    DEFAULT_PACE,
    DEFAULT_MEAL_STYLE,
    DEFAULT_TIME_PREFERENCE,
    SUPPORTED_IMAGE_MIME_TYPE,
)
import json
import logging
from typing import Optional
import typing_extensions as typing

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# Gemini Client Initialization
# ──────────────────────────────────────────────

if settings.GOOGLE_CLOUD_PROJECT:
    client = genai.Client(
        vertexai=True,
        project=settings.GOOGLE_CLOUD_PROJECT,
        location=settings.GOOGLE_CLOUD_LOCATION,
    )
else:
    client = genai.Client(api_key=settings.GEMINI_API_KEY)

# ──────────────────────────────────────────────
# TypedDict schemas for Gemini structured output
# ──────────────────────────────────────────────


class Destination(typing.TypedDict):
    """A suggested travel destination with city name and country."""
    name: str
    country: str


class PlaceSignal(typing.TypedDict):
    """A signal extracted from a mood board photo about trip intent.

    Attributes:
        type: Category of place (restaurant, landmark, neighborhood, hotel, activity).
        vibe: What this place signals about the traveler's intent.
    """
    type: str
    vibe: str


class VibeProfile(typing.TypedDict):
    """Structured output schema for mood board vibe analysis.

    Contains all extracted signals from uploaded inspiration photos,
    used to personalize itinerary generation.
    """
    tags: list[str]
    mood: str
    travel_style: str
    pace: str
    place_signals: list[PlaceSignal]
    must_haves: list[str]
    avoid_hints: list[str]
    suggested_destinations: list[Destination]
    meal_style: str
    time_of_day_preference: str


class TravelToNext(typing.TypedDict):
    """Transit information between consecutive stops."""
    duration: str
    mode: str


class Stop(typing.TypedDict):
    """A single stop in the day's itinerary with full detail."""
    time: str
    name: str
    description: str
    neighborhood: str
    wheelchair: bool
    vegetarian: bool
    stepFree: bool
    cost: str
    priceLevel: int
    streetViewUrl: str
    travelToNext: TravelToNext
    rainy_day_fallback: str


class DayPlan(typing.TypedDict):
    """A single day's plan with stops and total cost."""
    stops: list[Stop]
    totalCost: str


class ItineraryOutput(typing.TypedDict):
    """Complete itinerary output schema from Gemini."""
    days: list[DayPlan]
    conflicts_resolved: list[str]
    total_estimated_cost: float
    accessibility_notes: str


# ──────────────────────────────────────────────
# Analyze mood board photos → VibeProfile
# ──────────────────────────────────────────────

def analyze_vibe(images: list[bytes]) -> dict:
    """Analyze mood board photos to extract a structured travel vibe profile.

    Uses Gemini's multimodal capabilities to interpret uploaded travel
    inspiration photos and extract actionable signals: mood, pace, style,
    place signals, must-haves, avoid hints, and 3 suggested destinations.

    Args:
        images: List of raw image bytes (JPEG/PNG/WEBP). Max 6 images.

    Returns:
        A dict matching the VibeProfile schema with all extracted signals.
        Returns a default empty profile if no images are provided.
        Returns an error profile with diagnostic info if Gemini fails.

    Side effects:
        Makes one API call to the Gemini model per invocation.
        Logs analytics events to BigQuery when configured.
    """
    if not images:
        return {
            "tags": [], "mood": "", "travel_style": DEFAULT_TRAVEL_STYLE,
            "pace": DEFAULT_PACE, "place_signals": [], "must_haves": [],
            "avoid_hints": [], "suggested_destinations": [],
            "meal_style": DEFAULT_MEAL_STYLE, "time_of_day_preference": DEFAULT_TIME_PREFERENCE,
        }

    contents: list = [VIBE_ANALYSIS_SYSTEM_PROMPT]
    for img_bytes in images:
        contents.append(
            types.Part.from_bytes(data=img_bytes, mime_type=SUPPORTED_IMAGE_MIME_TYPE)
        )

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                response_mime_type=GEMINI_RESPONSE_MIME_TYPE,
                response_schema=VibeProfile,
                temperature=GEMINI_VIBE_TEMPERATURE,
            ),
        )
        result = json.loads(response.text)

        # Log analytics event (non-blocking, best-effort)
        try:
            from services.analytics_service import log_vibe_analyzed
            log_vibe_analyzed(
                vibe_tags=result.get("tags", []),
                travel_style=result.get("travel_style", ""),
                pace=result.get("pace", ""),
                num_images=len(images),
                suggested_destinations=result.get("suggested_destinations", []),
            )
        except Exception:
            pass  # Analytics should never break the main flow

        return result
    except Exception as e:
        logger.error("Gemini vibe error: %s", e)
        return {
            "tags": ["API Error"],
            "mood": "Unable to analyze",
            "travel_style": DEFAULT_TRAVEL_STYLE,
            "pace": DEFAULT_PACE,
            "place_signals": [],
            "must_haves": [],
            "avoid_hints": [],
            "suggested_destinations": [{"name": "Error", "country": str(e)}],
            "meal_style": DEFAULT_MEAL_STYLE,
            "time_of_day_preference": DEFAULT_TIME_PREFERENCE,
        }


# ──────────────────────────────────────────────
# Generate vibe-driven itinerary
# ──────────────────────────────────────────────

def generate_itinerary(constraints: dict, vibe: Optional[dict] = None) -> dict:
    """Generate a day-by-day travel itinerary using Gemini.

    Combines the user's hard constraints (destination, dates, budget,
    accessibility) with soft vibe preferences (mood, pace, meal style)
    to produce a conflict-resolved, geographically clustered itinerary.

    Args:
        constraints: Dict with required keys: destination, startDate, endDate,
            budget, currency, groupType, groupSize, accessibility.
            Optional: must_include, exclude, days.
        vibe: Optional VibeProfile dict from mood board analysis.
            Keys: mood, travel_style, pace, must_haves, avoid_hints,
            meal_style, time_of_day_preference, place_signals.

    Returns:
        A dict matching the ItineraryOutput schema with:
            - days: list of DayPlan objects with stops
            - conflicts_resolved: list of constraint resolution explanations
            - total_estimated_cost: float in the specified currency
            - accessibility_notes: string with accessibility guidance

    Side effects:
        Makes one API call to the Gemini model per invocation.
        Logs analytics events to BigQuery when configured.
        Persists the itinerary to Firestore when configured.
    """
    if vibe is None:
        vibe = {}

    # Calculate number of days from dates
    start: str = constraints.get("startDate", "")
    end: str = constraints.get("endDate", "")
    try:
        from datetime import datetime
        d1 = datetime.strptime(start, "%Y-%m-%d")
        d2 = datetime.strptime(end, "%Y-%m-%d")
        num_days: int = max(1, (d2 - d1).days + 1)
    except Exception:
        num_days = constraints.get("days", DEFAULT_NUM_DAYS)

    destination: str = constraints.get("destination", DEFAULT_DESTINATION)
    budget: float = constraints.get("budget", DEFAULT_BUDGET)
    currency: str = constraints.get("currency", DEFAULT_CURRENCY)
    group_type: str = constraints.get("groupType", DEFAULT_GROUP_TYPE)
    group_size: int = constraints.get("groupSize", DEFAULT_GROUP_SIZE)

    prompt = f"""{ITINERARY_SYSTEM_PROMPT}

VIBE PROFILE (what the person actually wants):
- Mood: {vibe.get('mood', 'Not specified')}
- Travel style: {vibe.get('travel_style', DEFAULT_TRAVEL_STYLE)}
- Inferred pace: {vibe.get('pace', DEFAULT_PACE)}
- Must-haves: {vibe.get('must_haves', [])}
- Avoid: {vibe.get('avoid_hints', [])}
- Meal style: {vibe.get('meal_style', DEFAULT_MEAL_STYLE)}
- Time of day preference: {vibe.get('time_of_day_preference', DEFAULT_TIME_PREFERENCE)}
- Place signals: {vibe.get('place_signals', [])}

CONSTRAINTS (hard limits):
- Destination: {destination}
- Number of days: {num_days}
- Start date: {start}
- End date: {end}
- Budget: {budget} {currency}
- Group: {group_type}, {group_size} people
- Accessibility: {constraints.get('accessibility', {})}
- Must include: {constraints.get('must_include', [])}
- Exclude: {constraints.get('exclude', [])}

Generate exactly {num_days} days.
"""

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_mime_type=GEMINI_RESPONSE_MIME_TYPE,
                response_schema=ItineraryOutput,
                temperature=GEMINI_ITINERARY_TEMPERATURE,
            ),
        )
        result: dict = json.loads(response.text)

        # Ensure total_estimated_cost is a float
        if isinstance(result.get("total_estimated_cost"), str):
            try:
                result["total_estimated_cost"] = float(
                    result["total_estimated_cost"]
                    .replace("€", "").replace("$", "")
                    .replace("£", "").replace(",", "").strip()
                )
            except Exception:
                result["total_estimated_cost"] = 0.0

        # Log analytics event (non-blocking, best-effort)
        try:
            from services.analytics_service import log_itinerary_generated
            log_itinerary_generated(
                destination=destination,
                num_days=num_days,
                budget=budget,
                currency=currency,
                group_type=group_type,
                group_size=group_size,
                vibe_tags=vibe.get("tags"),
                travel_style=vibe.get("travel_style"),
                pace=vibe.get("pace"),
            )
        except Exception:
            pass  # Analytics should never break the main flow

        # Persist to Firestore (non-blocking, best-effort)
        try:
            from services.firestore_service import save_itinerary
            meta = {
                "destination": destination,
                "startDate": start,
                "endDate": end,
                "numDays": num_days,
                "groupType": group_type,
                "groupSize": group_size,
                "currency": currency,
                "budget": budget,
            }
            save_itinerary(itinerary=result, meta=meta, vibe=vibe)
        except Exception:
            pass  # Persistence should never break the main flow

        return result
    except Exception as e:
        logger.error("Gemini itinerary error: %s", e)
        # Fallback mock
        return {
            "days": [
                {
                    "stops": [
                        {
                            "time": "10:00",
                            "name": "Historic City Center",
                            "description": "Start the day exploring the historic heart of the city.",
                            "neighborhood": "City Center",
                            "wheelchair": True,
                            "vegetarian": False,
                            "stepFree": True,
                            "cost": "Free",
                            "priceLevel": 0,
                            "streetViewUrl": "",
                            "travelToNext": {"duration": "15 min", "mode": "Walk"},
                            "rainy_day_fallback": "Visit the local history museum",
                        }
                    ],
                    "totalCost": "€50",
                }
            ] * max(1, num_days),
            "conflicts_resolved": [f"API Error: {str(e)}"],
            "total_estimated_cost": 50.0 * num_days,
            "accessibility_notes": "Please verify venue accessibility on arrival.",
        }
