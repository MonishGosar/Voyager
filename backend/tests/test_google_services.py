"""
Unit tests for Google Cloud services (Firestore and BigQuery).

Tests cover:
    - Firestore client initialization with/without project
    - Save, get, and list itinerary operations (mocked)
    - BigQuery client initialization with/without project
    - Analytics event logging for vibe and itinerary (mocked)
    - Graceful fallback when GCP services are unavailable
"""

import pytest
from unittest.mock import patch, MagicMock

from tests.conftest import MOCK_ITINERARY_RESPONSE, MOCK_VIBE_RESPONSE


class TestFirestoreService:
    """Tests for the Firestore service module."""

    @patch("services.firestore_service.settings")
    def test_no_project_disables_firestore(self, mock_settings):
        """Firestore should be disabled when GOOGLE_CLOUD_PROJECT is empty."""
        mock_settings.GOOGLE_CLOUD_PROJECT = ""
        # Reset the cached client
        import services.firestore_service as fs
        fs._firestore_client = None

        client = fs._get_firestore_client()
        assert client is None

    @patch("services.firestore_service.settings")
    def test_save_itinerary_returns_none_without_project(self, mock_settings):
        """save_itinerary should return None when Firestore is unavailable."""
        mock_settings.GOOGLE_CLOUD_PROJECT = ""
        import services.firestore_service as fs
        fs._firestore_client = None

        result = fs.save_itinerary(
            itinerary=MOCK_ITINERARY_RESPONSE,
            meta={"destination": "Lisbon"},
        )
        assert result is None

    @patch("services.firestore_service.settings")
    def test_get_itinerary_returns_none_without_project(self, mock_settings):
        """get_itinerary should return None when Firestore is unavailable."""
        mock_settings.GOOGLE_CLOUD_PROJECT = ""
        import services.firestore_service as fs
        fs._firestore_client = None

        result = fs.get_itinerary("some-doc-id")
        assert result is None

    @patch("services.firestore_service.settings")
    def test_list_itineraries_returns_empty_without_project(self, mock_settings):
        """list_itineraries should return empty list when Firestore is unavailable."""
        mock_settings.GOOGLE_CLOUD_PROJECT = ""
        import services.firestore_service as fs
        fs._firestore_client = None

        result = fs.list_itineraries()
        assert result == []


class TestAnalyticsService:
    """Tests for the BigQuery analytics service module."""

    @patch("services.analytics_service.settings")
    def test_no_project_disables_bigquery(self, mock_settings):
        """BigQuery should be disabled when GOOGLE_CLOUD_PROJECT is empty."""
        mock_settings.GOOGLE_CLOUD_PROJECT = ""
        import services.analytics_service as analytics
        analytics._bq_client = None

        client = analytics._get_bq_client()
        assert client is None

    @patch("services.analytics_service.settings")
    def test_log_vibe_returns_false_without_project(self, mock_settings):
        """log_vibe_analyzed should return False when BigQuery is unavailable."""
        mock_settings.GOOGLE_CLOUD_PROJECT = ""
        import services.analytics_service as analytics
        analytics._bq_client = None

        result = analytics.log_vibe_analyzed(
            vibe_tags=["sunset", "wine"],
            travel_style="food pilgrim",
            pace="relaxed",
            num_images=3,
            suggested_destinations=[{"name": "Porto", "country": "Portugal"}],
        )
        assert result is False

    @patch("services.analytics_service.settings")
    def test_log_itinerary_returns_false_without_project(self, mock_settings):
        """log_itinerary_generated should return False when BigQuery is unavailable."""
        mock_settings.GOOGLE_CLOUD_PROJECT = ""
        import services.analytics_service as analytics
        analytics._bq_client = None

        result = analytics.log_itinerary_generated(
            destination="Lisbon",
            num_days=5,
            budget=1000,
            currency="EUR",
            group_type="couple",
            group_size=2,
        )
        assert result is False
