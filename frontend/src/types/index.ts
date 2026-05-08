/**
 * Shared TypeScript type definitions for the Voyager frontend.
 *
 * These types mirror the backend Pydantic models exactly to ensure
 * frontend-backend alignment. Any change here must be reflected in
 * the corresponding backend model, and vice versa.
 *
 * @see backend/models/vibe.py — VibeProfile, PlaceSignal, Destination
 * @see backend/models/itinerary.py — Itinerary, DayPlan, Stop, TravelToNext
 * @see backend/models/constraints.py — PlanningConstraints
 */

// ──────────────────────────────────────────────
// Vibe Models (matches backend/models/vibe.py)
// ──────────────────────────────────────────────

/** A signal extracted from a mood board photo about trip intent. */
export interface PlaceSignal {
  /** Category: restaurant, landmark, neighborhood, hotel, or activity. */
  type: string;
  /** What this place signals about the traveler's preferences. */
  vibe: string;
}

/** A suggested travel destination inferred from mood board analysis. */
export interface Destination {
  /** City name (e.g. 'Porto'). */
  name: string;
  /** Country name (e.g. 'Portugal'). */
  country: string;
}

/**
 * Structured vibe profile extracted from mood board photos.
 *
 * Contains all signals the AI extracts from uploaded travel inspiration
 * images, used to personalize itinerary generation with soft preferences.
 */
export interface VibeProfile {
  /** 4-6 specific, sensory vibe tags (e.g. 'candlelit wine caves'). */
  tags: string[];
  /** One-sentence emotional summary of the desired trip. */
  mood: string;
  /** Closest travel style archetype. */
  travel_style: string;
  /** Inferred trip pace: 'relaxed', 'balanced', or 'packed'. */
  pace: string;
  /** List of place-intent signals from photos. */
  place_signals: PlaceSignal[];
  /** Inferred non-negotiable trip elements. */
  must_haves: string[];
  /** What's absent from the board (things to avoid). */
  avoid_hints: string[];
  /** 3 AI-matched destination cities. */
  suggested_destinations: Destination[];
  /** Inferred dining preference. */
  meal_style: string;
  /** Preferred time of day for activities. */
  time_of_day_preference: string;
}

// ──────────────────────────────────────────────
// Itinerary Models (matches backend/models/itinerary.py)
// ──────────────────────────────────────────────

/** Transit information between consecutive itinerary stops. */
export interface TravelToNext {
  /** Estimated travel time (e.g. '15 min'). */
  duration: string;
  /** Mode of transport (e.g. 'Walk', 'Metro', 'Taxi'). */
  mode: string;
}

/**
 * A single stop in the day's itinerary with full detail.
 *
 * Contains venue information, accessibility flags, cost data,
 * and a rainy day alternative for outdoor activities.
 */
export interface Stop {
  /** Scheduled arrival time (e.g. '10:00'). */
  time: string;
  /** Venue or place name. */
  name: string;
  /** Brief description of the activity or experience. */
  description: string;
  /** Neighborhood or district within the city. */
  neighborhood: string;
  /** Whether the venue is wheelchair accessible. */
  wheelchair: boolean;
  /** Whether vegetarian/vegan options are available. */
  vegetarian: boolean;
  /** Whether the venue has step-free access. */
  stepFree: boolean;
  /** Formatted cost string (e.g. '€15', 'Free'). */
  cost: string;
  /** Price level from 0 (free) to 4 (very expensive). */
  priceLevel: number;
  /** Google Street View URL for the venue. */
  streetViewUrl: string;
  /** Transit info to the next stop, if applicable. */
  travelToNext: TravelToNext | null;
  /** Indoor alternative if it rains. */
  rainy_day_fallback: string;
}

/** A single day's itinerary plan with ordered stops and total cost. */
export interface DayPlan {
  /** Ordered list of stops for the day. */
  stops: Stop[];
  /** Formatted total cost for the day (e.g. '€120'). */
  totalCost: string;
}

/**
 * Complete multi-day travel itinerary with conflict resolution.
 *
 * The top-level response model for the /api/plan endpoint, containing
 * the full day-by-day plan, constraint resolution log, and accessibility notes.
 */
export interface Itinerary {
  /** List of day plans, each containing ordered stops. */
  days: DayPlan[];
  /** Log of how vibe vs constraint conflicts were resolved. */
  conflicts_resolved: string[];
  /** Total trip cost as a float. */
  total_estimated_cost: number;
  /** Accessibility guidance for the entire trip. */
  accessibility_notes: string;
}

// ──────────────────────────────────────────────
// Constraint Models (matches backend/models/constraints.py)
// ──────────────────────────────────────────────

/**
 * User-provided constraints for itinerary generation.
 *
 * These are the hard limits that the AI must respect when building
 * the itinerary. Budget and accessibility always take priority over
 * vibe preferences when conflicts arise.
 */
export interface PlanningConstraints {
  /** Target city or region (e.g. 'Lisbon, Portugal'). */
  destination: string;
  /** Trip start date in YYYY-MM-DD format. */
  startDate: string;
  /** Trip end date in YYYY-MM-DD format. */
  endDate: string;
  /** Group type: solo, couple, friends, family. */
  groupType: string;
  /** Number of travelers. */
  groupSize: number;
  /** Budget currency code (USD, EUR, INR, GBP). */
  currency: string;
  /** Total trip budget in the specified currency. */
  budget: number;
  /** Travel pace on a 1-3 scale. */
  pace: number;
  /** Accessibility requirements. */
  accessibility: Record<string, boolean>;
  /** Specific venues or experiences to include. */
  must_include: string[];
  /** Venues or categories to exclude. */
  exclude: string[];
  /** Optional VibeProfile from mood board analysis step. */
  vibe: VibeProfile | null;
}

// ──────────────────────────────────────────────
// Client-side Meta Types
// ──────────────────────────────────────────────

/**
 * Trip metadata stored in sessionStorage for the itinerary page.
 *
 * This is a client-side type, not part of the API contract.
 */
export interface TripMeta {
  /** Destination city/region name. */
  destination: string;
  /** Trip start date (YYYY-MM-DD). */
  startDate: string;
  /** Trip end date (YYYY-MM-DD). */
  endDate: string;
  /** Calculated number of trip days. */
  numDays: number;
  /** Group type label. */
  groupType: string;
  /** Number of travelers. */
  groupSize: number;
  /** Currency code. */
  currency: string;
  /** Budget as a string (from input field). */
  budget: string;
}

// ──────────────────────────────────────────────
// API Error Response
// ──────────────────────────────────────────────

/**
 * Standard error response shape from the backend.
 *
 * All backend error handlers return this shape via JSONResponse.
 */
export interface ApiErrorResponse {
  /** Error category (e.g. 'validation_error', 'internal_server_error'). */
  error: string;
  /** Human-readable error message. */
  message: string;
  /** Optional validation error details (from Pydantic). */
  detail?: unknown[];
}
