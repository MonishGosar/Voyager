"""
Gemini AI service for travel vibe analysis and itinerary generation.

This module provides the core AI intelligence layer of Voyager, using
Google's Gemini 2.5 Flash model via the google-genai SDK. It handles:

    - Mood board photo analysis → structured VibeProfile extraction
    - Constraint-aware itinerary generation with conflict resolution

All prompts, model names, and configuration are sourced from constants.py
to ensure maintainability. Responses use Gemini's structured output mode
with TypedDict schemas for type safety.

Usage:
    from services.gemini_service import analyze_vibe, generate_itinerary

    profile = analyze_vibe([image_bytes_1, image_bytes_2])
    itinerary = generate_itinerary(constraints_dict, vibe_dict)
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
    DATE_FORMAT,
)
import json
import logging
from typing import Optional
import typing_extensions as typing

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# Gemini Client Initialization
# ──────────────────────────────────────────────

if settings.GEMINI_API_KEY:
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
elif settings.GOOGLE_CLOUD_PROJECT:
    client = genai.Client(
        vertexai=True,
        project=settings.GOOGLE_CLOUD_PROJECT,
        location=settings.GOOGLE_CLOUD_LOCATION,
    )
else:
    client = genai.Client(api_key="")

# ──────────────────────────────────────────────
# TypedDict schemas for Gemini structured output
# ──────────────────────────────────────────────


class Destination(typing.TypedDict):
    """A suggested travel destination with city name and country.

    Attributes:
        name: City name (e.g. 'Porto').
        country: Country name (e.g. 'Portugal').
    """

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

    Attributes:
        tags: 4-6 specific sensory vibe tags.
        mood: One-sentence emotional trip summary.
        travel_style: Closest travel style archetype.
        pace: Inferred trip pace (relaxed, balanced, packed).
        place_signals: List of place-intent signals from photos.
        must_haves: Inferred non-negotiable trip elements.
        avoid_hints: Things to avoid based on absence from board.
        suggested_destinations: 3 AI-matched destination cities.
        meal_style: Inferred dining preference.
        time_of_day_preference: Preferred time of day for activities.
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
    """Transit information between consecutive stops.

    Attributes:
        duration: Estimated travel time (e.g. '15 min').
        mode: Mode of transport (e.g. 'Walk', 'Metro', 'Taxi').
    """

    duration: str
    mode: str


class Stop(typing.TypedDict):
    """A single stop in the day's itinerary with full detail.

    Attributes:
        time: Scheduled arrival time (e.g. '10:00').
        name: Venue or place name.
        description: Brief description of the activity.
        neighborhood: Neighborhood or district within the city.
        wheelchair: Whether the venue is wheelchair accessible.
        vegetarian: Whether vegetarian/vegan options are available.
        stepFree: Whether the venue has step-free access.
        cost: Formatted cost string (e.g. '€15', 'Free').
        priceLevel: Price level from 0 (free) to 4 (very expensive).
        streetViewUrl: Google Street View URL for the venue.
        travelToNext: Transit info to the next stop.
        rainy_day_fallback: Indoor alternative if it rains.
    """

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
    """A single day's plan with stops and total cost.

    Attributes:
        stops: Ordered list of stops for the day.
        totalCost: Formatted total cost for the day.
    """

    stops: list[Stop]
    totalCost: str


class ItineraryOutput(typing.TypedDict):
    """Complete itinerary output schema from Gemini.

    Attributes:
        days: List of day plans, each containing ordered stops.
        conflicts_resolved: Log of how vibe vs constraint conflicts were resolved.
        total_estimated_cost: Total trip cost as a float.
        accessibility_notes: Accessibility guidance for the entire trip.
    """

    days: list[DayPlan]
    conflicts_resolved: list[str]
    total_estimated_cost: float
    accessibility_notes: str


# ──────────────────────────────────────────────
# Analyze mood board photos → VibeProfile
# ──────────────────────────────────────────────


def _build_default_vibe_profile() -> dict[str, object]:
    """Build a default empty vibe profile when no images are provided.

    Returns:
        A dict matching the VibeProfile schema with empty/default values.
    """
    return {
        "tags": [],
        "mood": "",
        "travel_style": DEFAULT_TRAVEL_STYLE,
        "pace": DEFAULT_PACE,
        "place_signals": [],
        "must_haves": [],
        "avoid_hints": [],
        "suggested_destinations": [],
        "meal_style": DEFAULT_MEAL_STYLE,
        "time_of_day_preference": DEFAULT_TIME_PREFERENCE,
    }


def _safe_ai_error_message(error: Exception) -> str:
    """Return a user-safe AI failure message without leaking provider details."""
    message = str(error)
    if "SERVICE_DISABLED" in message or "aiplatform.googleapis.com" in message:
        return "AI service is not enabled for this deployment."
    if "PERMISSION_DENIED" in message or "403" in message:
        return "AI service permission denied for this deployment."
    if "quota" in message.lower():
        return "AI service quota exceeded. Please try again later."
    return "AI service is temporarily unavailable. Please try again."


def _log_vibe_analytics(result: dict[str, object], num_images: int) -> None:
    """Log vibe analysis event to BigQuery (best-effort, non-blocking).

    Args:
        result: The parsed vibe profile dict from Gemini.
        num_images: Number of images that were analyzed.

    Side effects:
        Inserts a row into BigQuery if configured. Silently ignores errors.
    """
    try:
        from services.analytics_service import log_vibe_analyzed

        log_vibe_analyzed(
            vibe_tags=result.get("tags", []),
            travel_style=result.get("travel_style", ""),
            pace=result.get("pace", ""),
            num_images=num_images,
            suggested_destinations=result.get("suggested_destinations", []),
        )
    except ImportError:
        logger.debug("_log_vibe_analytics: analytics_service not available")
    except Exception as e:
        logger.debug("_log_vibe_analytics: analytics logging failed: %s", e)


def analyze_vibe(images: list[bytes]) -> dict[str, object]:
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

    Raises:
        No exceptions are raised — errors are caught and returned as
        degraded VibeProfile dicts with error information in tags/mood.
    """
    if not images:
        logger.info("analyze_vibe: no images provided, returning default profile")
        return _build_default_vibe_profile()

    contents: list[object] = [VIBE_ANALYSIS_SYSTEM_PROMPT]
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
        result: dict[str, object] = json.loads(response.text)

        # Log analytics event (non-blocking, best-effort)
        _log_vibe_analytics(result, len(images))

        return result

    except json.JSONDecodeError as e:
        logger.error("analyze_vibe: failed to parse Gemini JSON response: %s", e)
        error_profile = _build_default_vibe_profile()
        error_profile["tags"] = ["JSON Parse Error"]
        error_profile["mood"] = "Gemini returned malformed JSON"
        error_profile["suggested_destinations"] = [{"name": "Error", "country": "Malformed response"}]
        return error_profile

    except Exception as e:
        safe_message = _safe_ai_error_message(e)
        logger.error(
            "analyze_vibe: Gemini API call failed for %d images: %s",
            len(images),
            e,
        )
        error_profile = _build_default_vibe_profile()
        error_profile["tags"] = ["API Error"]
        error_profile["mood"] = "Unable to analyze"
        error_profile["suggested_destinations"] = [{"name": "Error", "country": safe_message}]
        return error_profile


# ──────────────────────────────────────────────
# Generate vibe-driven itinerary
# ──────────────────────────────────────────────


def _parse_num_days(constraints: dict[str, object]) -> int:
    """Calculate the number of trip days from start and end dates.

    Args:
        constraints: Dict containing 'startDate' and 'endDate' in YYYY-MM-DD format.

    Returns:
        Number of days (inclusive), or the fallback from constraints['days']
        or DEFAULT_NUM_DAYS if dates cannot be parsed.
    """
    start: str = constraints.get("startDate", "")
    end: str = constraints.get("endDate", "")
    try:
        from datetime import datetime

        d1 = datetime.strptime(start, DATE_FORMAT)
        d2 = datetime.strptime(end, DATE_FORMAT)
        return max(1, (d2 - d1).days + 1)
    except (ValueError, TypeError) as e:
        logger.warning(
            "_parse_num_days: could not parse dates (start=%s, end=%s): %s",
            start,
            end,
            e,
        )
        return constraints.get("days", DEFAULT_NUM_DAYS)


def _parse_estimated_cost(result: dict[str, object]) -> float:
    """Ensure total_estimated_cost is a float, stripping currency symbols.

    Args:
        result: The raw itinerary dict from Gemini.

    Returns:
        The total estimated cost as a float. Returns 0.0 if parsing fails.
    """
    raw_cost = result.get("total_estimated_cost")
    if isinstance(raw_cost, (int, float)):
        return float(raw_cost)
    if isinstance(raw_cost, str):
        try:
            return float(
                raw_cost.replace("€", "")
                .replace("$", "")
                .replace("£", "")
                .replace("₹", "")
                .replace(",", "")
                .strip()
            )
        except (ValueError, AttributeError) as e:
            logger.warning("_parse_estimated_cost: could not parse '%s': %s", raw_cost, e)
            return 0.0
    return 0.0


def _log_itinerary_analytics(
    destination: str,
    num_days: int,
    budget: float,
    currency: str,
    group_type: str,
    group_size: int,
    vibe: dict[str, object],
) -> None:
    """Log itinerary generation event to BigQuery (best-effort, non-blocking).

    Args:
        destination: Target destination city.
        num_days: Number of days in the itinerary.
        budget: Total trip budget.
        currency: Budget currency code.
        group_type: Group type (solo, couple, friends, family).
        group_size: Number of travelers.
        vibe: Vibe profile dict from mood board analysis.

    Side effects:
        Inserts a row into BigQuery if configured. Silently ignores errors.
    """
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
    except ImportError:
        logger.debug("_log_itinerary_analytics: analytics_service not available")
    except Exception as e:
        logger.debug("_log_itinerary_analytics: analytics logging failed: %s", e)


def _persist_itinerary(
    result: dict[str, object],
    destination: str,
    start: str,
    end: str,
    num_days: int,
    group_type: str,
    group_size: int,
    currency: str,
    budget: float,
    vibe: dict[str, object],
) -> None:
    """Persist itinerary to Firestore (best-effort, non-blocking).

    Args:
        result: The full itinerary dict.
        destination: Target destination city.
        start: Trip start date string.
        end: Trip end date string.
        num_days: Number of days in the itinerary.
        group_type: Group type.
        group_size: Number of travelers.
        currency: Budget currency code.
        budget: Total trip budget.
        vibe: Vibe profile dict.

    Side effects:
        Creates a document in Firestore if configured. Silently ignores errors.
    """
    try:
        from services.firestore_service import save_itinerary

        meta: dict[str, object] = {
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
    except ImportError:
        logger.debug("_persist_itinerary: firestore_service not available")
    except Exception as e:
        logger.debug("_persist_itinerary: Firestore persistence failed: %s", e)


def _build_fallback_itinerary(num_days: int, error_message: str) -> dict[str, object]:
    """Build a minimal fallback itinerary when Gemini fails.

    Args:
        num_days: Number of days to generate fallback stops for.
        error_message: The error message to include in conflicts_resolved.

    Returns:
        A dict matching the ItineraryOutput schema with one generic stop per day.
    """
    fallback_day: dict[str, object] = {
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
    return {
        "days": [fallback_day] * max(1, num_days),
        "conflicts_resolved": [f"API Error: {error_message}"],
        "total_estimated_cost": 50.0 * num_days,
        "accessibility_notes": "Please verify venue accessibility on arrival.",
    }


def generate_itinerary(
    constraints: dict[str, object],
    vibe: Optional[dict[str, object]] = None,
) -> dict[str, object]:
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

    Raises:
        No exceptions are raised — errors are caught and a fallback
        itinerary is returned with the error logged in conflicts_resolved.
    """
    if vibe is None:
        vibe = {}

    # Extract constraint values with defaults
    num_days: int = _parse_num_days(constraints)
    start: str = constraints.get("startDate", "")
    end: str = constraints.get("endDate", "")
    destination: str = constraints.get("destination", DEFAULT_DESTINATION)
    budget: float = constraints.get("budget", DEFAULT_BUDGET)
    currency: str = constraints.get("currency", DEFAULT_CURRENCY)
    group_type: str = constraints.get("groupType", DEFAULT_GROUP_TYPE)
    group_size: int = constraints.get("groupSize", DEFAULT_GROUP_SIZE)

    prompt: str = f"""{ITINERARY_SYSTEM_PROMPT}

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
        result: dict[str, object] = json.loads(response.text)

        # Ensure total_estimated_cost is a float
        result["total_estimated_cost"] = _parse_estimated_cost(result)

        # Log analytics event (non-blocking, best-effort)
        _log_itinerary_analytics(
            destination, num_days, budget, currency, group_type, group_size, vibe
        )

        # Persist to Firestore (non-blocking, best-effort)
        _persist_itinerary(
            result, destination, start, end, num_days,
            group_type, group_size, currency, budget, vibe,
        )

        return result

    except json.JSONDecodeError as e:
        logger.error(
            "generate_itinerary: failed to parse Gemini JSON for destination=%s: %s",
            destination,
            e,
        )
        return _build_fallback_itinerary(num_days, f"Malformed JSON from AI: {e}")

    except Exception as e:
        logger.error(
            "generate_itinerary: Gemini API call failed for destination=%s, %d days: %s",
            destination,
            num_days,
            e,
        )
        return _build_fallback_itinerary(num_days, str(e))
