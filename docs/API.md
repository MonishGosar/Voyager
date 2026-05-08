# API Contract Documentation

This document is the **single source of truth** for all API endpoints in the Voyager backend. Every request/response shape must match the corresponding Pydantic model (backend) and TypeScript interface + Zod schema (frontend) exactly.

---

## Base URL

- **Local development**: `http://localhost:8080`
- **Production (Cloud Run)**: `https://voyager-<project-hash>.<region>.run.app`

---

## Endpoints

### `GET /health`

Health check endpoint for Cloud Run readiness probes.

**Response** `200 OK`
```json
{
  "status": "ok"
}
```

---

### `POST /api/vibe`

Upload mood board photos for AI vibe analysis.

**Content-Type**: `multipart/form-data`

**Request**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `files` | `File[]` | Yes | 1-6 image files (JPEG, PNG, WEBP). Max 5MB each. |

**Response** `200 OK` — `VibeProfile`

```json
{
  "tags": ["candlelit wine caves", "fisherman's dock at 6am"],
  "mood": "A slow, wine-soaked week where nothing is rushed",
  "travel_style": "slow explorer",
  "pace": "balanced",
  "place_signals": [
    { "type": "restaurant", "vibe": "fine dining is non-negotiable" }
  ],
  "must_haves": ["at least one exceptional meal per day"],
  "avoid_hints": ["no museums"],
  "suggested_destinations": [
    { "name": "Porto", "country": "Portugal" },
    { "name": "Seville", "country": "Spain" },
    { "name": "Nice", "country": "France" }
  ],
  "meal_style": "local trattorias",
  "time_of_day_preference": "evening person"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `tags` | `string[]` | 4-6 specific sensory vibe tags |
| `mood` | `string` | One-sentence emotional trip summary |
| `travel_style` | `string` | One of: `slow explorer`, `food pilgrim`, `culture deep-dive`, `luxury leisure`, `adventure seeker` |
| `pace` | `string` | One of: `relaxed`, `balanced`, `packed` |
| `place_signals` | `PlaceSignal[]` | Array of `{ type: string, vibe: string }` |
| `must_haves` | `string[]` | Inferred non-negotiable trip elements |
| `avoid_hints` | `string[]` | Things to avoid (absent from board) |
| `suggested_destinations` | `Destination[]` | Array of `{ name: string, country: string }` — exactly 3 |
| `meal_style` | `string` | One of: `fine dining`, `street food`, `local trattorias`, `mixed` |
| `time_of_day_preference` | `string` | One of: `morning explorer`, `evening person`, `all-day` |

**Error Responses**

| Status | Body | When |
|--------|------|------|
| `400` | `{ "detail": "Maximum 6 images allowed. Received N." }` | Too many files uploaded |
| `413` | `{ "detail": "File 'name' exceeds the 5MB size limit." }` | File too large |
| `422` | `{ "detail": [...] }` | Missing required `files` field |
| `500` | `{ "detail": "Vibe analysis failed. Please try again." }` | Gemini API failure |

---

### `POST /api/plan`

Generate a vibe-driven, constraint-resolved travel itinerary.

**Content-Type**: `application/json`

**Request** — `PlanningConstraints`

```json
{
  "destination": "Lisbon, Portugal",
  "startDate": "2025-06-15",
  "endDate": "2025-06-19",
  "groupType": "couple",
  "groupSize": 2,
  "currency": "EUR",
  "budget": 2000.0,
  "pace": 2,
  "accessibility": { "wheelchair": false, "vegetarian": true },
  "must_include": [],
  "exclude": [],
  "vibe": null
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `destination` | `string` | Yes | Target city or region |
| `startDate` | `string` | Yes | Trip start date (YYYY-MM-DD) |
| `endDate` | `string` | Yes | Trip end date (YYYY-MM-DD) |
| `groupType` | `string` | Yes | One of: `solo`, `couple`, `friends`, `family` |
| `groupSize` | `integer` | Yes | 1-20 travelers |
| `currency` | `string` | Yes | One of: `USD`, `EUR`, `INR`, `GBP` |
| `budget` | `float` | Yes | Total trip budget (≥ 0) |
| `pace` | `integer` | No | 1 (relaxed), 2 (balanced), 3 (packed). Default: 2 |
| `accessibility` | `object` | No | Dict of `{ key: boolean }` flags |
| `must_include` | `string[]` | No | Venues to include |
| `exclude` | `string[]` | No | Venues to exclude |
| `vibe` | `VibeProfile \| null` | No | Vibe profile from Step 1 |

**Response** `200 OK` — `Itinerary`

```json
{
  "days": [
    {
      "stops": [
        {
          "time": "10:00",
          "name": "Pastéis de Belém",
          "description": "Start with the world-famous Portuguese tarts.",
          "neighborhood": "Belém",
          "wheelchair": true,
          "vegetarian": true,
          "stepFree": true,
          "cost": "€5",
          "priceLevel": 1,
          "streetViewUrl": "",
          "travelToNext": { "duration": "15 min", "mode": "Walk" },
          "rainy_day_fallback": "Visit MAAT museum across the street"
        }
      ],
      "totalCost": "€120"
    }
  ],
  "conflicts_resolved": [
    "Replaced rooftop bar with Miradouro da Graça — same view, no cover charge"
  ],
  "total_estimated_cost": 450.0,
  "accessibility_notes": "All selected venues have step-free access."
}
```

| Field | Type | Description |
|-------|------|-------------|
| `days` | `DayPlan[]` | Array of day plans |
| `days[].stops` | `Stop[]` | Ordered stops for the day |
| `days[].totalCost` | `string` | Formatted daily total cost |
| `days[].stops[].time` | `string` | Arrival time (e.g. '10:00') |
| `days[].stops[].name` | `string` | Venue name |
| `days[].stops[].description` | `string` | Activity description |
| `days[].stops[].neighborhood` | `string` | Neighborhood/district |
| `days[].stops[].wheelchair` | `boolean` | Wheelchair accessible |
| `days[].stops[].vegetarian` | `boolean` | Vegetarian options |
| `days[].stops[].stepFree` | `boolean` | Step-free access |
| `days[].stops[].cost` | `string` | Formatted cost string |
| `days[].stops[].priceLevel` | `integer` | 0 (free) to 4 (expensive) |
| `days[].stops[].streetViewUrl` | `string` | Street View URL (may be empty) |
| `days[].stops[].travelToNext` | `TravelToNext \| null` | Transit to next stop |
| `days[].stops[].rainy_day_fallback` | `string` | Indoor alternative |
| `conflicts_resolved` | `string[]` | How vibe vs. constraint conflicts were resolved |
| `total_estimated_cost` | `float` | Total trip cost |
| `accessibility_notes` | `string` | Trip-level accessibility guidance |

**Error Responses**

| Status | Body | When |
|--------|------|------|
| `422` | `{ "error": "validation_error", "detail": [...] }` | Invalid constraints |
| `500` | `{ "detail": "Itinerary generation failed." }` | Gemini API failure |

---

## Global Error Response Shape

All unhandled errors return:

```json
{
  "error": "internal_server_error",
  "message": "An unexpected error occurred. Please try again later."
}
```

Validation errors return:

```json
{
  "error": "validation_error",
  "detail": [ ... ],
  "message": "Request data failed validation."
}
```

---

## Frontend Validation

All API responses are validated at runtime on the frontend using Zod schemas defined in `frontend/src/lib/schemas.ts`. This catches contract mismatches before they cause rendering errors.

| Schema | File | Validates |
|--------|------|-----------|
| `VibeProfileSchema` | `lib/schemas.ts` | POST /api/vibe response |
| `ItinerarySchema` | `lib/schemas.ts` | POST /api/plan response |
| `ApiErrorSchema` | `lib/schemas.ts` | Error responses |
