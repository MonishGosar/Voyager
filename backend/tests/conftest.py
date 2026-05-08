"""
Shared pytest fixtures for the Voyager test suite.

Provides mock Gemini responses, test clients, and sample data
that can be reused across unit, integration, and workflow tests.
"""

import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

# ──────────────────────────────────────────────
# Sample data fixtures
# ──────────────────────────────────────────────

MOCK_VIBE_RESPONSE = {
    "tags": ["candlelit wine caves", "fisherman's dock at 6am", "tiled courtyard lunch", "sunset rooftop aperitivo"],
    "mood": "A slow, wine-soaked week where nothing is rushed and every meal takes two hours",
    "travel_style": "food pilgrim",
    "pace": "relaxed",
    "place_signals": [
        {"type": "restaurant", "vibe": "fine dining is non-negotiable"},
        {"type": "neighborhood", "vibe": "wants to wander, not just tick boxes"},
    ],
    "must_haves": ["at least one exceptional meal per day", "elevated views or rooftop access"],
    "avoid_hints": ["no museums", "no nightlife"],
    "suggested_destinations": [
        {"name": "Porto", "country": "Portugal"},
        {"name": "Bologna", "country": "Italy"},
        {"name": "San Sebastián", "country": "Spain"},
    ],
    "meal_style": "local trattorias",
    "time_of_day_preference": "evening person",
}

MOCK_ITINERARY_RESPONSE = {
    "days": [
        {
            "stops": [
                {
                    "time": "09:30",
                    "name": "Café A Brasileira",
                    "description": "Start with a galão at Lisbon's most iconic literary café.",
                    "neighborhood": "Chiado",
                    "wheelchair": True,
                    "vegetarian": True,
                    "stepFree": True,
                    "cost": "€5",
                    "priceLevel": 1,
                    "streetViewUrl": "",
                    "travelToNext": {"duration": "10 min", "mode": "Walk"},
                    "rainy_day_fallback": "Stay longer at the café and people-watch",
                },
                {
                    "time": "11:00",
                    "name": "Miradouro de Santa Catarina",
                    "description": "Sweeping views over the Tagus river and the 25 de Abril bridge.",
                    "neighborhood": "Bairro Alto",
                    "wheelchair": False,
                    "vegetarian": False,
                    "stepFree": False,
                    "cost": "Free",
                    "priceLevel": 0,
                    "streetViewUrl": "",
                    "travelToNext": {"duration": "15 min", "mode": "Walk"},
                    "rainy_day_fallback": "Visit the MAAT museum nearby",
                },
            ],
            "totalCost": "€45",
        },
        {
            "stops": [
                {
                    "time": "10:00",
                    "name": "Time Out Market",
                    "description": "Browse Lisbon's best food hall for a curated brunch.",
                    "neighborhood": "Cais do Sodré",
                    "wheelchair": True,
                    "vegetarian": True,
                    "stepFree": True,
                    "cost": "€20",
                    "priceLevel": 2,
                    "streetViewUrl": "",
                    "travelToNext": {"duration": "5 min", "mode": "Walk"},
                    "rainy_day_fallback": "Perfect indoor activity already",
                },
            ],
            "totalCost": "€65",
        },
    ],
    "conflicts_resolved": [
        "Replaced Belém Tower on Day 1 with Miradouro de Santa Catarina — same elevated view, closer to accommodation"
    ],
    "total_estimated_cost": 110.0,
    "accessibility_notes": "Most stops in Chiado and Bairro Alto have cobblestone streets. Day 1 stops are wheelchair accessible.",
}

SAMPLE_CONSTRAINTS = {
    "destination": "Lisbon",
    "startDate": "2026-06-01",
    "endDate": "2026-06-03",
    "groupType": "couple",
    "groupSize": 2,
    "currency": "EUR",
    "budget": 500.0,
    "pace": 2,
    "accessibility": {"wheelchair": False, "vegetarian": True},
    "must_include": [],
    "exclude": [],
    "vibe": MOCK_VIBE_RESPONSE,
}


@pytest.fixture
def mock_vibe_response():
    """Fixture providing a realistic mock Gemini vibe analysis response."""
    return MOCK_VIBE_RESPONSE.copy()


@pytest.fixture
def mock_itinerary_response():
    """Fixture providing a realistic mock Gemini itinerary response."""
    return MOCK_ITINERARY_RESPONSE.copy()


@pytest.fixture
def sample_constraints():
    """Fixture providing sample planning constraints for testing."""
    return SAMPLE_CONSTRAINTS.copy()


@pytest.fixture
def test_client():
    """Fixture providing a FastAPI TestClient with mocked Gemini calls."""
    from main import app
    return TestClient(app)


@pytest.fixture
def mock_gemini_client():
    """Fixture that patches the Gemini client for unit testing.

    Prevents actual API calls to Gemini during tests.
    """
    with patch("services.gemini_service.client") as mock_client:
        yield mock_client
