"""
Constants and configuration values for the Voyager backend.

Centralizes all hardcoded strings, model names, API endpoints, prompt templates,
and cache configuration to improve maintainability and prevent magic strings.
"""

# ──────────────────────────────────────────────
# Gemini Model Configuration
# ──────────────────────────────────────────────

GEMINI_MODEL: str = "gemini-2.5-flash"
"""The Gemini model identifier used for all AI inference calls."""

GEMINI_VIBE_TEMPERATURE: float = 0.7
"""Temperature setting for vibe analysis — slightly creative."""

GEMINI_ITINERARY_TEMPERATURE: float = 0.8
"""Temperature setting for itinerary generation — balanced creativity."""

GEMINI_RESPONSE_MIME_TYPE: str = "application/json"
"""MIME type for structured JSON responses from Gemini."""

# ──────────────────────────────────────────────
# API Endpoints
# ──────────────────────────────────────────────

API_PREFIX: str = "/api"
"""Base prefix for all API routes."""

NOMINATIM_SEARCH_URL: str = "https://nominatim.openstreetmap.org/search"
"""OpenStreetMap Nominatim geocoding endpoint."""

# ──────────────────────────────────────────────
# Cache Configuration
# ──────────────────────────────────────────────

PLACES_CACHE_TTL_SECONDS: int = 3600
"""Time-to-live for Places API response cache (1 hour)."""

PLACES_CACHE_MAX_SIZE: int = 512
"""Maximum entries in the Places LRU cache."""

GEOCODE_CACHE_TTL_SECONDS: int = 86400
"""Time-to-live for geocoding cache (24 hours)."""

# ──────────────────────────────────────────────
# Firestore Configuration
# ──────────────────────────────────────────────

FIRESTORE_ITINERARIES_COLLECTION: str = "itineraries"
"""Firestore collection name for persisted itineraries."""

FIRESTORE_EVENTS_COLLECTION: str = "analytics_events"
"""Firestore collection name for analytics events."""

# ──────────────────────────────────────────────
# BigQuery Configuration
# ──────────────────────────────────────────────

BIGQUERY_DATASET: str = "voyager_analytics"
"""BigQuery dataset for trip planning analytics."""

BIGQUERY_EVENTS_TABLE: str = "trip_events"
"""BigQuery table for anonymized trip planning events."""

# ──────────────────────────────────────────────
# Default Values
# ──────────────────────────────────────────────

DEFAULT_DESTINATION: str = "Lisbon"
"""Default destination when none is specified."""

DEFAULT_NUM_DAYS: int = 3
"""Fallback number of days when dates cannot be parsed."""

DEFAULT_BUDGET: int = 1000
"""Default budget in USD when not specified."""

DEFAULT_CURRENCY: str = "USD"
"""Default currency code."""

DEFAULT_GROUP_TYPE: str = "couple"
"""Default group type."""

DEFAULT_GROUP_SIZE: int = 2
"""Default group size."""

DEFAULT_TRAVEL_STYLE: str = "slow explorer"
"""Default travel style for vibe profiles."""

DEFAULT_PACE: str = "balanced"
"""Default pace for itineraries."""

DEFAULT_MEAL_STYLE: str = "mixed"
"""Default meal style preference."""

DEFAULT_TIME_PREFERENCE: str = "all-day"
"""Default time-of-day preference."""

# ──────────────────────────────────────────────
# Image Processing
# ──────────────────────────────────────────────

MAX_UPLOAD_IMAGES: int = 6
"""Maximum number of mood board images per upload."""

SUPPORTED_IMAGE_MIME_TYPE: str = "image/jpeg"
"""Default MIME type for uploaded images."""

# ──────────────────────────────────────────────
# Travel Styles (valid enum values)
# ──────────────────────────────────────────────

VALID_TRAVEL_STYLES: list[str] = [
    "slow explorer",
    "food pilgrim",
    "culture deep-dive",
    "luxury leisure",
    "adventure seeker",
]

VALID_PACES: list[str] = ["relaxed", "balanced", "packed"]

VALID_MEAL_STYLES: list[str] = ["fine dining", "street food", "local trattorias", "mixed"]

VALID_TIME_PREFERENCES: list[str] = ["morning explorer", "evening person", "all-day"]

# ──────────────────────────────────────────────
# Prompt Templates
# ──────────────────────────────────────────────

VIBE_ANALYSIS_SYSTEM_PROMPT: str = """
You are analyzing a mood board of travel inspiration photos.
The person didn't pick these randomly — every photo signals something about what they actually want from a trip.
Your job is to read between the lines, not just describe what you see.

WHAT TO EXTRACT:

1. Tags (4-6): Specific and sensory. Not adjectives — moments.
   Good: "candlelit wine caves", "fisherman's dock at 6am", "tiled courtyard lunch"
   Bad: "romantic", "cultural", "good food"

2. Mood (1 sentence): What does this trip feel like emotionally?
   E.g. "A slow, wine-soaked week where nothing is rushed and every meal takes two hours"

3. Travel style — pick the single closest:
   "slow explorer" / "food pilgrim" / "culture deep-dive" / "luxury leisure" / "adventure seeker"

4. Pace — infer from photo density and venue types:
   "relaxed" (few hero spots, lots of wandering)
   "balanced" (mix of landmarks and downtime)
   "packed" (many specific venues, grid-style planning)

5. Place signals — for each distinct photo type, what does it signal?
   A Michelin restaurant photo signals: fine dining is non-negotiable
   A Pinterest-saved neighborhood street signals: wants to wander, not just tick boxes
   A specific hotel lobby signals: accommodation matters to them
   A hiking trail signals: physical activity expected

6. Must-haves — infer from what appears repeatedly or prominently.
   If 3 photos show food: "at least one exceptional meal per day"
   If photos show rooftops: "elevated views or rooftop access"

7. Avoid hints — what is completely absent from their board?
   No museums → probably not a museum person
   No beaches → likely wants urban or inland
   No nightlife → morning/afternoon focused traveler

8. Exactly 3 suggested destinations: the cities that satisfy the most signals simultaneously.
   Not the most famous cities — the most accurate ones.

9. Meal style: infer from the food/restaurant photos present.
   Options: "fine dining" | "street food" | "local trattorias" | "mixed"

10. Time of day preference:
    Golden hour photos = "evening person"
    Market photos = "morning explorer"
    Otherwise = "all-day"

Return ONLY valid JSON. No explanation.
"""

ITINERARY_SYSTEM_PROMPT: str = """You are building a day-by-day travel itinerary. You have two inputs:
a VIBE PROFILE (what the person actually wants) and CONSTRAINTS (hard limits).

ITINERARY RULES — follow these exactly:

1. PACE LOGIC
   - "relaxed": max 3 stops per day, at least 2 hours at each, nothing before 9am
   - "balanced": 4-5 stops per day, mix of long and short stays
   - "packed": 5-7 stops per day, tight transitions, early starts acceptable

2. TIME OF DAY LOGIC
   - "morning explorer": markets, bakeries, and walks before 10am. Wind down by 8pm.
   - "evening person": slow mornings, golden hour stops locked in at 6-7pm, dinner after 8pm
   - "all-day": balanced distribution

3. MEAL PLACEMENT
   - meal_style = "fine dining": one long lunch OR dinner per day (not both), 90 min minimum
   - meal_style = "street food": 2-3 short food stops distributed across the day
   - meal_style = "local trattorias": lunch 1-2pm only, dinner 7:30pm+, no tourist traps
   - Always name specific real venues, never "a local restaurant"

4. CONFLICT RESOLUTION — when vibe and constraints conflict:
   - Budget beats vibe preference (always)
   - Accessibility beats everything (always)
   - When you drop something, log it in conflicts_resolved with the reason
   - E.g. "Replaced rooftop bar on Day 2 with Miradouro da Graça — same elevated view, no cover charge"

5. MUST-HAVES PLACEMENT
   - Distribute must-haves across different days, not all on day 1
   - Place the single best experience on day 2 or 3 — not day 1 (they're still adjusting)
   - Save one highlight for the second-to-last day (last day is usually packing/transit)

6. SMART DAY STRUCTURE
   - Day 1: arrival-friendly, nothing requiring booking, nearby the accommodation area
   - Last day: half-day only, airport/station transfer friendly timing
   - Rainy day alternatives: note one indoor fallback per day if outdoor activity is primary

7. GEOGRAPHIC LOGIC
   - Cluster stops by neighborhood per day — never bounce across the city
   - Walking radius max 2km per day unless transit is explicitly in the plan
   - Transit stops need travel time logged accurately

Return valid JSON only. Every stop must have: time, name, description, neighborhood,
wheelchair (bool), vegetarian (bool), stepFree (bool), cost (string), priceLevel (0-4 int),
streetViewUrl (empty string ok), travelToNext (object with duration and mode strings),
rainy_day_fallback (string — an alternative if it rains).
"""
