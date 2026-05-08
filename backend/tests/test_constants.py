"""
Unit tests for the constants module.

Tests cover:
    - All constants are defined and non-empty
    - Default values are sensible
    - Prompt templates contain expected keywords
    - Enum lists are non-empty and contain expected values
"""

import pytest

from constants import (
    GEMINI_MODEL,
    GEMINI_VIBE_TEMPERATURE,
    GEMINI_ITINERARY_TEMPERATURE,
    GEMINI_RESPONSE_MIME_TYPE,
    API_PREFIX,
    PLACES_CACHE_TTL_SECONDS,
    PLACES_CACHE_MAX_SIZE,
    FIRESTORE_ITINERARIES_COLLECTION,
    BIGQUERY_DATASET,
    BIGQUERY_EVENTS_TABLE,
    DEFAULT_DESTINATION,
    DEFAULT_NUM_DAYS,
    DEFAULT_BUDGET,
    VALID_TRAVEL_STYLES,
    VALID_PACES,
    VALID_MEAL_STYLES,
    VALID_TIME_PREFERENCES,
    VIBE_ANALYSIS_SYSTEM_PROMPT,
    ITINERARY_SYSTEM_PROMPT,
    MAX_UPLOAD_IMAGES,
)


class TestConstants:
    """Tests for the constants module."""

    def test_gemini_model_is_set(self):
        """Gemini model name should be a non-empty string."""
        assert isinstance(GEMINI_MODEL, str)
        assert len(GEMINI_MODEL) > 0
        assert "gemini" in GEMINI_MODEL.lower()

    def test_temperatures_in_range(self):
        """Temperature values should be between 0 and 2."""
        assert 0.0 <= GEMINI_VIBE_TEMPERATURE <= 2.0
        assert 0.0 <= GEMINI_ITINERARY_TEMPERATURE <= 2.0

    def test_response_mime_type(self):
        """Response MIME type should be application/json."""
        assert GEMINI_RESPONSE_MIME_TYPE == "application/json"

    def test_api_prefix(self):
        """API prefix should start with /."""
        assert API_PREFIX.startswith("/")

    def test_cache_config_positive(self):
        """Cache config values should be positive integers."""
        assert PLACES_CACHE_TTL_SECONDS > 0
        assert PLACES_CACHE_MAX_SIZE > 0

    def test_firestore_collection_names(self):
        """Firestore collection names should be non-empty strings."""
        assert isinstance(FIRESTORE_ITINERARIES_COLLECTION, str)
        assert len(FIRESTORE_ITINERARIES_COLLECTION) > 0

    def test_bigquery_names(self):
        """BigQuery dataset and table names should be non-empty strings."""
        assert isinstance(BIGQUERY_DATASET, str)
        assert len(BIGQUERY_DATASET) > 0
        assert isinstance(BIGQUERY_EVENTS_TABLE, str)
        assert len(BIGQUERY_EVENTS_TABLE) > 0

    def test_default_values_are_sensible(self):
        """Default values should be reasonable for a travel app."""
        assert DEFAULT_DESTINATION != ""
        assert DEFAULT_NUM_DAYS >= 1
        assert DEFAULT_BUDGET > 0
        assert MAX_UPLOAD_IMAGES >= 1

    def test_valid_enums_non_empty(self):
        """Enum lists should contain expected values."""
        assert "slow explorer" in VALID_TRAVEL_STYLES
        assert "balanced" in VALID_PACES
        assert "mixed" in VALID_MEAL_STYLES
        assert "all-day" in VALID_TIME_PREFERENCES

    def test_vibe_prompt_contains_keywords(self):
        """Vibe analysis prompt should mention key extraction tasks."""
        assert "mood board" in VIBE_ANALYSIS_SYSTEM_PROMPT.lower()
        assert "tags" in VIBE_ANALYSIS_SYSTEM_PROMPT.lower()
        assert "destinations" in VIBE_ANALYSIS_SYSTEM_PROMPT.lower()
        assert "json" in VIBE_ANALYSIS_SYSTEM_PROMPT.lower()

    def test_itinerary_prompt_contains_keywords(self):
        """Itinerary prompt should mention key generation rules."""
        assert "itinerary" in ITINERARY_SYSTEM_PROMPT.lower()
        assert "pace" in ITINERARY_SYSTEM_PROMPT.lower()
        assert "budget" in ITINERARY_SYSTEM_PROMPT.lower()
        assert "accessibility" in ITINERARY_SYSTEM_PROMPT.lower()
