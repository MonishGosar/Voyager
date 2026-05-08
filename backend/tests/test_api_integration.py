"""
Integration tests for API endpoints.

Tests cover:
    - GET /health returns 200 with status ok
    - POST /api/vibe returns 422 without files
    - POST /api/vibe with mock images returns valid VibeProfile
    - POST /api/plan with valid constraints returns valid Itinerary
    - POST /api/plan with missing fields returns 422
    - POST /api/plan with vibe profile returns enriched itinerary
    - POST /api/plan response has correct structure and types
"""

import json
import io
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from main import app
from tests.conftest import MOCK_VIBE_RESPONSE, MOCK_ITINERARY_RESPONSE, SAMPLE_CONSTRAINTS


client = TestClient(app)


class TestHealthEndpoint:
    """Tests for the /health endpoint."""

    def test_health_check_returns_ok(self):
        """GET /health should return 200 with status ok."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestVibeEndpoint:
    """Tests for the POST /api/vibe endpoint."""

    def test_vibe_without_files_returns_422(self):
        """POST /api/vibe without files should return 422 validation error."""
        response = client.post("/api/vibe")
        assert response.status_code == 422

    @patch("services.gemini_service.client")
    def test_vibe_with_images_returns_profile(self, mock_gemini):
        """POST /api/vibe with images should return a valid VibeProfile."""
        mock_response = MagicMock()
        mock_response.text = json.dumps(MOCK_VIBE_RESPONSE)
        mock_gemini.models.generate_content.return_value = mock_response

        # Create fake image file
        fake_image = io.BytesIO(b"\xff\xd8\xff\xe0" + b"\x00" * 100)
        fake_image.name = "test.jpg"

        response = client.post(
            "/api/vibe",
            files=[("files", ("test.jpg", fake_image, "image/jpeg"))],
        )
        assert response.status_code == 200
        data = response.json()
        assert "tags" in data
        assert "suggested_destinations" in data
        assert "mood" in data
        assert "travel_style" in data

    @patch("services.gemini_service.client")
    def test_vibe_response_structure(self, mock_gemini):
        """Vibe response should have all expected VibeProfile fields."""
        mock_response = MagicMock()
        mock_response.text = json.dumps(MOCK_VIBE_RESPONSE)
        mock_gemini.models.generate_content.return_value = mock_response

        fake_image = io.BytesIO(b"\xff\xd8\xff\xe0" + b"\x00" * 100)
        response = client.post(
            "/api/vibe",
            files=[("files", ("photo.jpg", fake_image, "image/jpeg"))],
        )
        data = response.json()

        required_fields = [
            "tags", "mood", "travel_style", "pace", "place_signals",
            "must_haves", "avoid_hints", "suggested_destinations",
            "meal_style", "time_of_day_preference",
        ]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"


class TestPlanEndpoint:
    """Tests for the POST /api/plan endpoint."""

    @patch("services.gemini_service.client")
    def test_plan_with_valid_constraints(self, mock_gemini):
        """POST /api/plan with valid constraints should return an Itinerary."""
        mock_response = MagicMock()
        mock_response.text = json.dumps(MOCK_ITINERARY_RESPONSE)
        mock_gemini.models.generate_content.return_value = mock_response

        response = client.post("/api/plan", json=SAMPLE_CONSTRAINTS)
        assert response.status_code == 200
        data = response.json()
        assert "days" in data
        assert "conflicts_resolved" in data
        assert "total_estimated_cost" in data
        assert "accessibility_notes" in data

    def test_plan_missing_fields_returns_422(self):
        """POST /api/plan with missing required fields should return 422."""
        incomplete = {"destination": "Rome"}
        response = client.post("/api/plan", json=incomplete)
        assert response.status_code == 422

    @patch("services.gemini_service.client")
    def test_plan_response_has_stops(self, mock_gemini):
        """Plan response should contain days with stops."""
        mock_response = MagicMock()
        mock_response.text = json.dumps(MOCK_ITINERARY_RESPONSE)
        mock_gemini.models.generate_content.return_value = mock_response

        response = client.post("/api/plan", json=SAMPLE_CONSTRAINTS)
        data = response.json()

        assert len(data["days"]) > 0
        first_day = data["days"][0]
        assert "stops" in first_day
        assert "totalCost" in first_day
        assert len(first_day["stops"]) > 0

        first_stop = first_day["stops"][0]
        assert "time" in first_stop
        assert "name" in first_stop
        assert "description" in first_stop
        assert "cost" in first_stop
        assert "wheelchair" in first_stop

    @patch("services.gemini_service.client")
    def test_plan_cost_is_numeric(self, mock_gemini):
        """total_estimated_cost should be a number, not a string."""
        mock_response = MagicMock()
        mock_response.text = json.dumps(MOCK_ITINERARY_RESPONSE)
        mock_gemini.models.generate_content.return_value = mock_response

        response = client.post("/api/plan", json=SAMPLE_CONSTRAINTS)
        data = response.json()
        assert isinstance(data["total_estimated_cost"], (int, float))

    @patch("services.gemini_service.client")
    def test_plan_without_vibe(self, mock_gemini):
        """Planning without vibe profile should still work."""
        mock_response = MagicMock()
        mock_response.text = json.dumps(MOCK_ITINERARY_RESPONSE)
        mock_gemini.models.generate_content.return_value = mock_response

        constraints_no_vibe = SAMPLE_CONSTRAINTS.copy()
        constraints_no_vibe["vibe"] = None

        response = client.post("/api/plan", json=constraints_no_vibe)
        assert response.status_code == 200
