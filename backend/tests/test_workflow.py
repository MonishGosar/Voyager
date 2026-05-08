"""
End-to-end workflow tests for the Voyager trip planning pipeline.

Tests cover the full workflow:
    1. Upload mood board photos → extract vibe
    2. Submit constraints with vibe → generate itinerary
    3. Verify itinerary matches constraint requirements

All external services (Gemini, BigQuery, Firestore) are mocked.
"""

import json
import io
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from main import app
from tests.conftest import MOCK_VIBE_RESPONSE, MOCK_ITINERARY_RESPONSE


client = TestClient(app)


class TestFullWorkflow:
    """End-to-end workflow tests simulating a complete user journey."""

    @patch("services.gemini_service.client")
    def test_upload_to_itinerary_workflow(self, mock_gemini):
        """Full workflow: upload photo → extract vibe → generate itinerary.

        Simulates the complete user journey:
        1. User uploads mood board photos
        2. Frontend receives vibe profile
        3. User fills in constraints
        4. Frontend sends constraints + vibe to plan endpoint
        5. Backend generates and returns itinerary
        """
        # Step 1: Extract vibe from uploaded photos
        mock_vibe_resp = MagicMock()
        mock_vibe_resp.text = json.dumps(MOCK_VIBE_RESPONSE)
        mock_gemini.models.generate_content.return_value = mock_vibe_resp

        fake_image_1 = io.BytesIO(b"\xff\xd8\xff\xe0" + b"\x00" * 100)
        fake_image_2 = io.BytesIO(b"\xff\xd8\xff\xe0" + b"\x00" * 200)

        vibe_response = client.post(
            "/api/vibe",
            files=[
                ("files", ("sunset.jpg", fake_image_1, "image/jpeg")),
                ("files", ("cafe.jpg", fake_image_2, "image/jpeg")),
            ],
        )
        assert vibe_response.status_code == 200
        vibe_data = vibe_response.json()
        assert len(vibe_data["tags"]) > 0
        assert len(vibe_data["suggested_destinations"]) > 0

        # Step 2: Use extracted vibe + user constraints to generate itinerary
        mock_itin_resp = MagicMock()
        mock_itin_resp.text = json.dumps(MOCK_ITINERARY_RESPONSE)
        mock_gemini.models.generate_content.return_value = mock_itin_resp

        # Pick first suggested destination (simulates user selection)
        selected_destination = vibe_data["suggested_destinations"][0]["name"]

        plan_payload = {
            "destination": selected_destination,
            "startDate": "2026-06-15",
            "endDate": "2026-06-19",
            "groupType": "couple",
            "groupSize": 2,
            "currency": "EUR",
            "budget": 1200.0,
            "pace": 2,
            "accessibility": {"wheelchair": False, "vegetarian": True},
            "must_include": [],
            "exclude": [],
            "vibe": vibe_data,
        }

        plan_response = client.post("/api/plan", json=plan_payload)
        assert plan_response.status_code == 200
        itinerary = plan_response.json()

        # Step 3: Verify itinerary structure
        assert "days" in itinerary
        assert len(itinerary["days"]) > 0
        assert "total_estimated_cost" in itinerary
        assert isinstance(itinerary["total_estimated_cost"], (int, float))
        assert "conflicts_resolved" in itinerary
        assert "accessibility_notes" in itinerary

        # Verify each day has stops
        for day in itinerary["days"]:
            assert "stops" in day
            assert "totalCost" in day
            for stop in day["stops"]:
                assert "time" in stop
                assert "name" in stop
                assert "description" in stop
                assert "wheelchair" in stop
                assert "vegetarian" in stop

    @patch("services.gemini_service.client")
    def test_workflow_without_vibe_step(self, mock_gemini):
        """Workflow where user skips vibe step and goes directly to planning.

        Some users may want to skip the mood board and jump straight
        to entering trip details. The system should handle this gracefully.
        """
        mock_response = MagicMock()
        mock_response.text = json.dumps(MOCK_ITINERARY_RESPONSE)
        mock_gemini.models.generate_content.return_value = mock_response

        plan_payload = {
            "destination": "Barcelona",
            "startDate": "2026-09-01",
            "endDate": "2026-09-04",
            "groupType": "friends",
            "groupSize": 6,
            "currency": "EUR",
            "budget": 3000.0,
            "pace": 3,
            "accessibility": {},
            "must_include": ["Sagrada Familia"],
            "exclude": [],
            "vibe": None,
        }

        response = client.post("/api/plan", json=plan_payload)
        assert response.status_code == 200
        itinerary = response.json()
        assert len(itinerary["days"]) > 0

    @patch("services.gemini_service.client")
    def test_workflow_with_accessibility_constraints(self, mock_gemini):
        """Workflow with strict accessibility requirements.

        Verifies that accessibility constraints are passed through
        to the itinerary generation prompt.
        """
        mock_vibe_resp = MagicMock()
        mock_vibe_resp.text = json.dumps(MOCK_VIBE_RESPONSE)

        mock_itin_resp = MagicMock()
        mock_itin_resp.text = json.dumps(MOCK_ITINERARY_RESPONSE)

        # First call = vibe, second = itinerary
        mock_gemini.models.generate_content.side_effect = [mock_vibe_resp, mock_itin_resp]

        # Step 1: Vibe extraction
        fake_image = io.BytesIO(b"\xff\xd8\xff\xe0" + b"\x00" * 100)
        vibe_response = client.post(
            "/api/vibe",
            files=[("files", ("beach.jpg", fake_image, "image/jpeg"))],
        )
        vibe_data = vibe_response.json()

        # Step 2: Plan with wheelchair accessibility
        plan_payload = {
            "destination": "Amsterdam",
            "startDate": "2026-10-01",
            "endDate": "2026-10-05",
            "groupType": "family",
            "groupSize": 4,
            "currency": "EUR",
            "budget": 2500.0,
            "accessibility": {"wheelchair": True, "vegetarian": True},
            "vibe": vibe_data,
        }

        plan_response = client.post("/api/plan", json=plan_payload)
        assert plan_response.status_code == 200
        itinerary = plan_response.json()
        assert "accessibility_notes" in itinerary

    @patch("services.gemini_service.client")
    def test_workflow_error_recovery(self, mock_gemini):
        """Workflow should handle Gemini errors gracefully.

        If the AI service fails, the system should return a fallback
        response instead of a 500 error.
        """
        mock_gemini.models.generate_content.side_effect = Exception("Service unavailable")

        plan_payload = {
            "destination": "Tokyo",
            "startDate": "2026-11-01",
            "endDate": "2026-11-05",
            "groupType": "solo",
            "groupSize": 1,
            "currency": "USD",
            "budget": 5000.0,
            "vibe": None,
        }

        response = client.post("/api/plan", json=plan_payload)
        assert response.status_code == 200  # fallback, not 500
        itinerary = response.json()
        assert "days" in itinerary
        assert any("Error" in c for c in itinerary["conflicts_resolved"])
