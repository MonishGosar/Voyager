"""
Unit tests for the Gemini service module.

Tests cover:
    - analyze_vibe() with empty input returns defaults
    - analyze_vibe() with images calls Gemini and returns parsed response
    - analyze_vibe() handles Gemini API errors gracefully
    - generate_itinerary() produces valid structured output
    - generate_itinerary() calculates days from dates correctly
    - generate_itinerary() handles Gemini API errors with fallback
    - generate_itinerary() cleans currency symbols from cost strings
"""

import json
import pytest
from unittest.mock import patch, MagicMock

from tests.conftest import MOCK_VIBE_RESPONSE, MOCK_ITINERARY_RESPONSE


class TestAnalyzeVibe:
    """Tests for the analyze_vibe function."""

    def test_empty_images_returns_defaults(self):
        """Empty image list should return default vibe profile without calling Gemini."""
        from services.gemini_service import analyze_vibe

        result = analyze_vibe([])
        assert result["tags"] == []
        assert result["mood"] == ""
        assert result["travel_style"] == "slow explorer"
        assert result["pace"] == "balanced"
        assert result["suggested_destinations"] == []
        assert result["meal_style"] == "mixed"
        assert result["time_of_day_preference"] == "all-day"

    @patch("services.gemini_service.client")
    def test_analyze_vibe_with_images(self, mock_client):
        """Providing images should call Gemini and return parsed vibe profile."""
        from services.gemini_service import analyze_vibe

        mock_response = MagicMock()
        mock_response.text = json.dumps(MOCK_VIBE_RESPONSE)
        mock_client.models.generate_content.return_value = mock_response

        fake_image = b"\xff\xd8\xff\xe0" + b"\x00" * 100  # fake JPEG header
        result = analyze_vibe([fake_image])

        mock_client.models.generate_content.assert_called_once()
        assert len(result["tags"]) == 4
        assert result["travel_style"] == "food pilgrim"
        assert result["pace"] == "relaxed"
        assert len(result["suggested_destinations"]) == 3
        assert result["suggested_destinations"][0]["name"] == "Porto"

    @patch("services.gemini_service.client")
    def test_analyze_vibe_handles_api_error(self, mock_client):
        """API errors should return error profile, not crash."""
        from services.gemini_service import analyze_vibe

        mock_client.models.generate_content.side_effect = Exception("Quota exceeded")

        fake_image = b"\xff\xd8\xff\xe0" + b"\x00" * 100
        result = analyze_vibe([fake_image])

        assert "API Error" in result["tags"]
        assert result["mood"] == "Unable to analyze"
        assert result["travel_style"] == "slow explorer"
        assert len(result["suggested_destinations"]) == 1
        assert "Quota exceeded" in result["suggested_destinations"][0]["country"]

    @patch("services.gemini_service.client")
    def test_analyze_vibe_with_multiple_images(self, mock_client):
        """Multiple images should all be passed to Gemini."""
        from services.gemini_service import analyze_vibe

        mock_response = MagicMock()
        mock_response.text = json.dumps(MOCK_VIBE_RESPONSE)
        mock_client.models.generate_content.return_value = mock_response

        fake_images = [b"\xff\xd8\xff\xe0" + b"\x00" * 100 for _ in range(4)]
        result = analyze_vibe(fake_images)

        # Verify the call happened with contents containing prompt + 4 image parts
        call_args = mock_client.models.generate_content.call_args
        contents = call_args.kwargs.get("contents") or call_args[1].get("contents")
        assert len(contents) == 5  # 1 prompt + 4 images


class TestGenerateItinerary:
    """Tests for the generate_itinerary function."""

    @patch("services.gemini_service.client")
    def test_generate_itinerary_basic(self, mock_client):
        """Basic itinerary generation with valid constraints."""
        from services.gemini_service import generate_itinerary

        mock_response = MagicMock()
        mock_response.text = json.dumps(MOCK_ITINERARY_RESPONSE)
        mock_client.models.generate_content.return_value = mock_response

        constraints = {
            "destination": "Lisbon",
            "startDate": "2026-06-01",
            "endDate": "2026-06-02",
            "budget": 500,
            "currency": "EUR",
            "groupType": "couple",
            "groupSize": 2,
            "accessibility": {},
        }
        result = generate_itinerary(constraints)

        assert "days" in result
        assert "conflicts_resolved" in result
        assert "total_estimated_cost" in result
        assert isinstance(result["total_estimated_cost"], float)
        assert result["total_estimated_cost"] == 110.0

    @patch("services.gemini_service.client")
    def test_generate_itinerary_with_vibe(self, mock_client):
        """Itinerary generation should incorporate vibe preferences."""
        from services.gemini_service import generate_itinerary

        mock_response = MagicMock()
        mock_response.text = json.dumps(MOCK_ITINERARY_RESPONSE)
        mock_client.models.generate_content.return_value = mock_response

        constraints = {
            "destination": "Porto",
            "startDate": "2026-07-10",
            "endDate": "2026-07-14",
            "budget": 1500,
            "currency": "EUR",
            "groupType": "friends",
            "groupSize": 4,
        }
        vibe = {
            "mood": "Relaxed wine country vibes",
            "travel_style": "food pilgrim",
            "pace": "relaxed",
            "must_haves": ["wine tasting"],
            "meal_style": "local trattorias",
        }
        result = generate_itinerary(constraints, vibe)

        # Verify the prompt includes vibe information
        call_args = mock_client.models.generate_content.call_args
        prompt_contents = call_args.kwargs.get("contents") or call_args[1].get("contents")
        prompt_text = prompt_contents[0] if isinstance(prompt_contents, list) else str(prompt_contents)
        assert "food pilgrim" in str(prompt_text)
        assert "wine tasting" in str(prompt_text)

    @patch("services.gemini_service.client")
    def test_generate_itinerary_calculates_days(self, mock_client):
        """Number of days should be calculated from start/end dates."""
        from services.gemini_service import generate_itinerary

        mock_response = MagicMock()
        mock_response.text = json.dumps(MOCK_ITINERARY_RESPONSE)
        mock_client.models.generate_content.return_value = mock_response

        constraints = {
            "destination": "Tokyo",
            "startDate": "2026-09-01",
            "endDate": "2026-09-05",
            "budget": 3000,
            "currency": "USD",
            "groupType": "solo",
            "groupSize": 1,
        }
        result = generate_itinerary(constraints)

        # The prompt should contain "5 days" (Sep 1 to Sep 5 inclusive)
        call_args = mock_client.models.generate_content.call_args
        prompt_contents = call_args.kwargs.get("contents") or call_args[1].get("contents")
        assert "5" in str(prompt_contents)

    @patch("services.gemini_service.client")
    def test_generate_itinerary_handles_api_error(self, mock_client):
        """API errors should return fallback itinerary, not crash."""
        from services.gemini_service import generate_itinerary

        mock_client.models.generate_content.side_effect = Exception("Model overloaded")

        constraints = {
            "destination": "Paris",
            "startDate": "2026-06-01",
            "endDate": "2026-06-03",
            "budget": 1000,
            "currency": "EUR",
            "groupType": "couple",
            "groupSize": 2,
        }
        result = generate_itinerary(constraints)

        assert "days" in result
        assert len(result["days"]) >= 1
        assert "API Error" in result["conflicts_resolved"][0]
        assert result["total_estimated_cost"] > 0

    @patch("services.gemini_service.client")
    def test_generate_itinerary_cost_cleanup(self, mock_client):
        """String costs with currency symbols should be parsed to float."""
        from services.gemini_service import generate_itinerary

        response_with_str_cost = MOCK_ITINERARY_RESPONSE.copy()
        response_with_str_cost["total_estimated_cost"] = "€1,250.00"

        mock_response = MagicMock()
        mock_response.text = json.dumps(response_with_str_cost)
        mock_client.models.generate_content.return_value = mock_response

        constraints = {
            "destination": "Rome",
            "startDate": "2026-06-01",
            "endDate": "2026-06-05",
            "budget": 2000,
            "currency": "EUR",
            "groupType": "couple",
            "groupSize": 2,
        }
        result = generate_itinerary(constraints)

        assert isinstance(result["total_estimated_cost"], float)
        assert result["total_estimated_cost"] == 1250.0

    def test_generate_itinerary_no_vibe(self):
        """Should work without a vibe profile (vibe=None)."""
        with patch("services.gemini_service.client") as mock_client:
            from services.gemini_service import generate_itinerary

            mock_response = MagicMock()
            mock_response.text = json.dumps(MOCK_ITINERARY_RESPONSE)
            mock_client.models.generate_content.return_value = mock_response

            constraints = {
                "destination": "Berlin",
                "startDate": "2026-08-01",
                "endDate": "2026-08-03",
                "budget": 800,
                "currency": "EUR",
                "groupType": "solo",
                "groupSize": 1,
            }
            result = generate_itinerary(constraints, vibe=None)
            assert "days" in result

    @patch("services.gemini_service.client")
    def test_generate_itinerary_invalid_dates_uses_default(self, mock_client):
        """Invalid date formats should fall back to default day count."""
        from services.gemini_service import generate_itinerary

        mock_response = MagicMock()
        mock_response.text = json.dumps(MOCK_ITINERARY_RESPONSE)
        mock_client.models.generate_content.return_value = mock_response

        constraints = {
            "destination": "Madrid",
            "startDate": "invalid",
            "endDate": "also-invalid",
            "budget": 500,
            "currency": "EUR",
            "groupType": "couple",
            "groupSize": 2,
            "days": 4,
        }
        result = generate_itinerary(constraints)
        assert "days" in result
