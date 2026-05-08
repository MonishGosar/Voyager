# 🧭 Voyager

**The world's first constraint-solving, vibe-reading travel intelligence engine.**

TripMind Voyager is a full-stack Next.js 14 and FastAPI application that builds a real, accessible, calendar-ready itinerary based on your uploaded mood board and exact constraints, grounded in live Google API data.

---

## 🏗️ Architecture

### System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                            │
│                                                                 │
│  ┌──────────┐    ┌──────────────┐    ┌───────────────────┐     │
│  │ VibeBoard│───>│ConstraintForm│───>│  ItineraryView    │     │
│  │ (Step 1) │    │  (Step 2)    │    │  (Step 3 + Map)   │     │
│  └────┬─────┘    └──────┬───────┘    └───────────────────┘     │
│       │                 │                                       │
│       │  Zod validates  │  Zod validates                       │
│       │  API responses  │  API responses                       │
└───────┼─────────────────┼───────────────────────────────────────┘
        │ POST /api/vibe  │ POST /api/plan
        ▼                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FASTAPI BACKEND                            │
│                                                                 │
│  ┌──────────────┐   ┌──────────────────────────┐               │
│  │  main.py     │   │  gemini_service.py        │               │
│  │  (CORS,      │──>│  (Vibe analysis +         │               │
│  │   Routers,   │   │   Itinerary generation)   │               │
│  │   Error      │   └──────────┬───────┬────────┘               │
│  │   Handlers)  │              │       │                        │
│  └──────────────┘              │       │                        │
│                                ▼       ▼                        │
│  ┌─────────────────┐  ┌──────────┐  ┌──────────────┐          │
│  │ firestore_svc   │  │ cache.py │  │ analytics_svc│          │
│  │ (Persistence)   │  │ (TTL)    │  │ (Events)     │          │
│  └────────┬────────┘  └──────────┘  └──────┬───────┘          │
└───────────┼─────────────────────────────────┼──────────────────┘
            │                                 │
            ▼                                 ▼
┌────────────────────┐             ┌──────────────────┐
│  Google Cloud      │             │  Google BigQuery  │
│  Firestore         │             │  (Analytics)      │
│  (Itinerary Store) │             │                   │
└────────────────────┘             └──────────────────┘

           ┌──────────────────────────────────────┐
           │         GOOGLE GEMINI 2.5 FLASH      │
           │    (Multimodal AI — vibe + itinerary) │
           └──────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------| 
| **Frontend** | Next.js 14 (App Router) + Tailwind CSS + shadcn/ui | Responsive UI with 3-step wizard |
| **Backend** | FastAPI (Python 3.11) | REST API with Pydantic validation |
| **AI Engine** | Gemini 2.5 Flash (`google-genai` SDK) | Multimodal vibe analysis + itinerary generation |
| **Persistence** | Google Cloud Firestore | Itinerary storage and retrieval |
| **Analytics** | Google BigQuery | Anonymized trip planning event logging |
| **Caching** | In-memory TTL cache | Reduces redundant API calls |
| **Validation** | Zod (frontend) + Pydantic (backend) | Runtime API contract enforcement |
| **Deployment** | Google Cloud Run | Single-container deployment under $5 budget |

---

## 🔌 Google APIs & Services Used

| Service | What It Does | Where Used |
|---------|-------------|------------|
| **Gemini 2.5 Flash** | Multimodal AI for vibe extraction + itinerary generation | `services/gemini_service.py` |
| **Google Maps JavaScript API** | Interactive map rendering on itinerary page | `ItineraryView.tsx` (via Leaflet/OSM) |
| **Google Calendar API** | "Add to Google Calendar" deep link generation | `ItineraryView.tsx` → `buildGoogleCalendarUrl()` |
| **Google Cloud Firestore** | Persist generated itineraries for retrieval | `services/firestore_service.py` |
| **Google BigQuery** | Log anonymized trip events for analytics | `services/analytics_service.py` |
| **Google Cloud Run** | Serverless container deployment | `Dockerfile` |

---

## 🏃 Local Development

### Prerequisites

- **Python** 3.11+
- **Node.js** 18+ and npm
- A Google Gemini API key (from [AI Studio](https://aistudio.google.com/))

### 1. Clone and configure environment

```bash
git clone https://github.com/MonishGosar/Voyager.git
cd voyager
cp .env.example .env
# Edit .env with your API keys (see Environment Variables section below)
```

### 2. Start the backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate          # Windows
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

The API server starts at `http://localhost:8080`. Verify with:
```bash
curl http://localhost:8080/health
# → {"status": "ok"}
```

### 3. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

The Next.js dev server starts at `http://localhost:3000` (or `3001` if 3000 is in use).

---

## 🔐 Environment Variables

Create a `.env` file in the project root (or copy from `.env.example`):

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes* | API key for Google Gemini (AI Studio mode). Get one from [AI Studio](https://aistudio.google.com/). Required unless `GOOGLE_CLOUD_PROJECT` is set. |
| `GOOGLE_MAPS_API_KEY` | No | API key for Google Maps/Places APIs. Used for map rendering. |
| `GOOGLE_CLOUD_PROJECT` | No | GCP project ID. Enables Firestore persistence and BigQuery analytics. Gemini uses Vertex AI only when `GEMINI_API_KEY` is not set. |
| `GOOGLE_CLOUD_LOCATION` | No | GCP region for Vertex AI and BigQuery (default: `us-central1`). |

\* Either `GEMINI_API_KEY` or `GOOGLE_CLOUD_PROJECT` must be set for AI features to work.

---

## ⚡ Performance & Caching

| Optimization | Before | After | Impact |
|-------------|--------|-------|--------|
| **Gemini prompt extraction** | System prompt rebuilt per request | Shared constant in `constants.py` | ~10ms per call |
| **TTL Cache for Places** | Every geocode = 1 API call (~200ms) | Cached results, 1h TTL | ~80% fewer API calls |
| **Geocode Cache** | Repeated city lookups hit network | 24h TTL cache | <1ms for repeated lookups |

Cache implementation: `services/cache.py` — thread-safe `TTLCache` with configurable TTL and max-size eviction.

---

## 🧪 Testing

### Running all tests

```bash
cd backend
pytest
```

Run with verbose output and coverage:
```bash
pytest -v --tb=short
```

Run only fast tests (skip integration tests):
```bash
pytest -m "not integration"
```

### Test Suite Coverage

| Suite | Tests | What It Covers |
|-------|-------|----------------|
| `test_constants.py` | 12 | Constants validation — model names, prompt keywords, valid value lists |
| `test_cache.py` | 12 | TTL cache — set/get, expiration, thread safety, eviction |
| `test_models.py` | 12 | Pydantic model validation — required fields, defaults, constraints |
| `test_gemini_service.py` | 9 | Gemini service — mocked AI responses, error handling, fallbacks |
| `test_google_services.py` | 7 | Firestore & BigQuery — graceful fallback when GCP unavailable |
| `test_api_integration.py` | 9 | API endpoints — health check, vibe upload, plan generation |
| `test_workflow.py` | 4 | End-to-end workflow — vibe → plan → itinerary pipeline |

### Type Checking (Backend)

```bash
cd backend
pip install pyright
pyright .
```

Configuration is in `pyproject.toml` under `[tool.pyright]`.

See [`tests/README.md`](backend/tests/README.md) for detailed test documentation.

---

## ☁️ Cloud Run Deployment

This repository is optimized to be deployed to Google Cloud Run as a single container, easily staying under a $5 GCP budget.

The `Dockerfile` handles building the Next.js static export and serving it via FastAPI.

### Steps to Deploy:

1. Enable the required APIs in GCP: Cloud Run API, Cloud Build API, Artifact Registry API, Firestore API, BigQuery API.
2. Ensure you have the `gcloud` CLI installed and authenticated.
3. Deploy directly using the source:
   ```bash
   gcloud run deploy tripmind-voyager \
     --source . \
     --region us-central1 \
     --allow-unauthenticated \
     --memory 512Mi \
     --set-env-vars="GEMINI_API_KEY=your_gemini_key,GOOGLE_MAPS_API_KEY=your_maps_key,GOOGLE_CLOUD_PROJECT=your_project_id"
   ```
4. You will get a Cloud Run URL!

---

## 📁 Project Structure

```
voyager/
├── frontend/                    # Next.js 14 App Router
│   └── src/
│       ├── app/                 # Pages (/, /vibe, /plan, /itinerary)
│       ├── components/          # React components
│       │   ├── vibe/            # VibeBoard (photo upload + AI analysis)
│       │   ├── plan/            # ConstraintForm (trip constraints)
│       │   ├── landing/         # LandingHero (landing page)
│       │   └── itinerary/       # ItineraryView (day-by-day plan + map)
│       ├── types/               # TypeScript interfaces (single source of truth)
│       │   └── index.ts         # All shared types
│       └── lib/                 # Utilities
│           └── schemas.ts       # Zod schemas for runtime API validation
├── backend/                     # FastAPI Python backend
│   ├── main.py                  # App entry + CORS + global exception handlers
│   ├── config.py                # Settings from env vars (pydantic-settings)
│   ├── constants.py             # All constants, prompts, config values
│   ├── pyproject.toml           # Pytest + Pyright config
│   ├── models/                  # Pydantic request/response schemas
│   │   ├── vibe.py              # VibeProfile, PlaceSignal, Destination
│   │   ├── constraints.py       # PlanningConstraints
│   │   └── itinerary.py         # Itinerary, DayPlan, Stop, TravelToNext
│   ├── routers/                 # API endpoint routers
│   │   ├── vibe.py              # POST /api/vibe
│   │   └── plan.py              # POST /api/plan
│   ├── services/                # Business logic layer
│   │   ├── gemini_service.py    # Gemini AI (vibe + itinerary)
│   │   ├── firestore_service.py # Firestore persistence
│   │   ├── analytics_service.py # BigQuery event logging
│   │   └── cache.py             # In-memory TTL cache
│   └── tests/                   # Comprehensive test suite (65+ tests)
│       ├── conftest.py          # Shared fixtures + mock data
│       ├── test_gemini_service.py
│       ├── test_cache.py
│       ├── test_models.py
│       ├── test_constants.py
│       ├── test_google_services.py
│       ├── test_api_integration.py
│       ├── test_workflow.py
│       └── README.md            # Test documentation
├── docs/
│   └── API.md                   # API contract documentation (source of truth)
├── Dockerfile                   # Cloud Run deployment
├── .env.example                 # Environment variable template
└── README.md                    # This file
```
