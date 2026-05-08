"""
Unit tests for Pydantic data models.

Tests cover:
    - VibeProfile validation with valid and partial data
    - PlanningConstraints validation and defaults
    - Itinerary / DayPlan / Stop model construction
    - Field validation constraints (ge, le bounds)
    - Model serialization (model_dump)
"""

import pytest
from pydantic import ValidationError

from models.vibe import VibeProfile, PlaceSignal, Destination
from models.constraints import PlanningConstraints
from models.itinerary import Itinerary, DayPlan, Stop, TravelToNext


class TestVibeProfileModel:
    """Tests for the VibeProfile Pydantic model."""

    def test_valid_full_profile(self):
        """Full vibe profile with all fields should pass validation."""
        profile = VibeProfile(
            tags=["sunset rooftop", "cobblestone alleys"],
            mood="Relaxed and romantic",
            travel_style="slow explorer",
            pace="relaxed",
            place_signals=[PlaceSignal(type="restaurant", vibe="fine dining")],
            must_haves=["wine tasting"],
            avoid_hints=["museums"],
            suggested_destinations=[
                Destination(name="Porto", country="Portugal"),
                Destination(name="Rome", country="Italy"),
            ],
            meal_style="local trattorias",
            time_of_day_preference="evening person",
        )
        assert len(profile.tags) == 2
        assert profile.travel_style == "slow explorer"

    def test_minimal_profile_with_defaults(self):
        """Profile with only required fields should use defaults."""
        profile = VibeProfile(
            tags=["adventure"],
            suggested_destinations=[Destination(name="Tokyo", country="Japan")],
        )
        assert profile.mood == ""
        assert profile.travel_style == "slow explorer"
        assert profile.pace == "balanced"
        assert profile.meal_style == "mixed"

    def test_empty_tags_is_valid(self):
        """Empty tags list should be valid."""
        profile = VibeProfile(
            tags=[],
            suggested_destinations=[Destination(name="Test", country="Test")],
        )
        assert profile.tags == []

    def test_place_signal_construction(self):
        """PlaceSignal should validate type and vibe strings."""
        signal = PlaceSignal(type="landmark", vibe="wants iconic photos")
        assert signal.type == "landmark"
        assert signal.vibe == "wants iconic photos"


class TestPlanningConstraintsModel:
    """Tests for the PlanningConstraints Pydantic model."""

    def test_valid_constraints(self):
        """Full constraints with all fields should pass validation."""
        constraints = PlanningConstraints(
            destination="Lisbon",
            startDate="2026-06-01",
            endDate="2026-06-05",
            groupType="couple",
            groupSize=2,
            currency="EUR",
            budget=1000.0,
        )
        assert constraints.destination == "Lisbon"
        assert constraints.pace == 2  # default
        assert constraints.accessibility == {}  # default
        assert constraints.vibe is None  # default

    def test_constraints_with_vibe(self):
        """Constraints with vibe profile should preserve the dict."""
        vibe = {"mood": "relaxed", "tags": ["sunset"]}
        constraints = PlanningConstraints(
            destination="Tokyo",
            startDate="2026-07-01",
            endDate="2026-07-10",
            groupType="solo",
            groupSize=1,
            currency="USD",
            budget=3000,
            vibe=vibe,
        )
        assert constraints.vibe == vibe

    def test_constraints_serialization(self):
        """model_dump() should produce a valid dict."""
        constraints = PlanningConstraints(
            destination="Paris",
            startDate="2026-08-01",
            endDate="2026-08-03",
            groupType="friends",
            groupSize=4,
            currency="EUR",
            budget=2000,
        )
        data = constraints.model_dump()
        assert isinstance(data, dict)
        assert data["destination"] == "Paris"
        assert data["groupSize"] == 4

    def test_missing_required_field_raises(self):
        """Missing required fields should raise ValidationError."""
        with pytest.raises(ValidationError):
            PlanningConstraints(
                destination="Rome",
                startDate="2026-06-01",
                # missing endDate, groupType, groupSize, currency, budget
            )


class TestItineraryModel:
    """Tests for the Itinerary Pydantic model."""

    def test_valid_itinerary(self):
        """Full itinerary with all fields should pass validation."""
        stop = Stop(
            time="10:00",
            name="Test Place",
            description="A great spot",
            cost="€10",
            priceLevel=2,
            streetViewUrl="",
            wheelchair=True,
            vegetarian=False,
            stepFree=True,
        )
        day = DayPlan(stops=[stop], totalCost="€50")
        itinerary = Itinerary(
            days=[day],
            conflicts_resolved=["Test conflict"],
            total_estimated_cost=50.0,
            accessibility_notes="All accessible",
        )
        assert len(itinerary.days) == 1
        assert itinerary.days[0].stops[0].name == "Test Place"

    def test_stop_with_travel_to_next(self):
        """Stop with travelToNext should validate the nested model."""
        stop = Stop(
            time="14:00",
            name="Museum",
            description="Art gallery",
            cost="€15",
            priceLevel=2,
            streetViewUrl="",
            travelToNext=TravelToNext(duration="10 min", mode="Walk"),
        )
        assert stop.travelToNext.duration == "10 min"
        assert stop.travelToNext.mode == "Walk"

    def test_stop_defaults(self):
        """Stop should have sensible defaults for optional fields."""
        stop = Stop(
            time="09:00",
            name="Café",
            description="Morning coffee",
            cost="€5",
            priceLevel=1,
            streetViewUrl="",
        )
        assert stop.neighborhood == ""
        assert stop.wheelchair is False
        assert stop.vegetarian is False
        assert stop.stepFree is False
        assert stop.travelToNext is None
        assert stop.rainy_day_fallback == ""

    def test_price_level_bounds(self):
        """priceLevel should be between 0 and 4."""
        # Valid
        stop = Stop(
            time="10:00", name="Test", description="Test",
            cost="Free", priceLevel=0, streetViewUrl="",
        )
        assert stop.priceLevel == 0

        stop = Stop(
            time="10:00", name="Test", description="Test",
            cost="€200", priceLevel=4, streetViewUrl="",
        )
        assert stop.priceLevel == 4
