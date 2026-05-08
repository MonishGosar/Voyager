# 🧭 Voyager

**The world's first constraint-solving, vibe-reading travel intelligence engine.**

TripMind Voyager is a full-stack Next.js 14 and FastAPI application that builds a real, accessible, calendar-ready itinerary based on your uploaded mood board and exact constraints, grounded in live Google API data.

---

## 🏗️ Architecture

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Next.js 14 (App Router) + Tailwind CSS + shadcn/ui | Responsive UI with 3-step wizard |
| **Backend** | FastAPI (Python 3.11) | REST API with Pydantic validation |
| **AI Engine** | Gemini 2.5 Flash (`google-genai` SDK) | Multimodal vibe analysis + itinerary generation |
| **Persistence** | Google Cloud Firestore | Itinerary storage and retrieval |
| **Analytics** | Google BigQuery | Anonymized trip planning event logging |
| **Caching** | In-memory TTL cache | Reduces redundant API calls |
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

## ⚡ Performance & Caching

| Optimization | Before | After | Impact |
|-------------|--------|-------|--------|
| **Gemini prompt extraction** | System prompt rebuilt per request | Shared constant in `constants.py` | ~10ms per call |
| **TTL Cache for Places** | Every geocode = 1 API call (~200ms) | Cached results, 1h TTL | ~80% fewer API calls |
| **Geocode Cache** | Repeated city lookups hit network | 24h TTL cache | <1ms for repeated lookups |

Cache implementation: `services/cache.py` — thread-safe `TTLCache` with configurable TTL and max-size eviction.

---

## 🧪 Testing

Run the full test suite from the backend directory:

```bash
cd backend
pytest
```

| Suite | Tests | Coverage |
|-------|-------|----------|
| `test_constants.py` | 12 | Constants validation, prompt keywords |
| `test_cache.py` | 12 | TTL cache: set/get, expiration, eviction |
| `test_models.py` | 12 | Pydantic model validation and defaults |
| `test_gemini_service.py` | 9 | Gemini service with mocked AI responses |
| `test_google_services.py` | 7 | Firestore & BigQuery graceful fallback |
| `test_api_integration.py` | 9 | API endpoint integration tests |
| `test_workflow.py` | 4 | End-to-end workflow tests |

See [`tests/README.md`](backend/tests/README.md) for detailed documentation.

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

## 🏃 Running Locally

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

### Environment Variables

```env
GEMINI_API_KEY=your_gemini_api_key
GOOGLE_MAPS_API_KEY=your_maps_api_key
GOOGLE_CLOUD_PROJECT=your_gcp_project_id  # Optional: enables Firestore + BigQuery
GOOGLE_CLOUD_LOCATION=us-central1          # Optional: BigQuery/Vertex location
```

---

## 📁 Project Structure

```
voyager/
├── frontend/                    # Next.js 14 App Router
│   └── src/
│       ├── app/                 # Pages (/, /plan, /itinerary)
│       └── components/          # React components
│           ├── vibe/            # VibeBoard (photo upload + AI analysis)
│           ├── plan/            # ConstraintForm (trip constraints)
│           └── itinerary/       # ItineraryView (day-by-day plan + map)
├── backend/                     # FastAPI Python backend
│   ├── main.py                  # App entry point with CORS + routers
│   ├── config.py                # Settings from env vars
│   ├── constants.py             # All constants, prompts, config values
│   ├── models/                  # Pydantic request/response schemas
│   │   ├── vibe.py              # VibeProfile model
│   │   ├── constraints.py       # PlanningConstraints model
│   │   └── itinerary.py         # Itinerary/DayPlan/Stop models
│   ├── routers/                 # API endpoint routers
│   │   ├── vibe.py              # POST /api/vibe
│   │   └── plan.py              # POST /api/plan
│   ├── services/                # Business logic layer
│   │   ├── gemini_service.py    # Gemini AI (vibe + itinerary)
│   │   ├── firestore_service.py # Firestore persistence
│   │   ├── analytics_service.py # BigQuery event logging
│   │   └── cache.py             # In-memory TTL cache
│   └── tests/                   # Comprehensive test suite
│       ├── conftest.py          # Shared fixtures + mock data
│       ├── test_gemini_service.py
│       ├── test_cache.py
│       ├── test_models.py
│       ├── test_constants.py
│       ├── test_google_services.py
│       ├── test_api_integration.py
│       ├── test_workflow.py
│       └── README.md            # Test documentation
├── Dockerfile                   # Cloud Run deployment
├── .env.example                 # Environment variable template
└── README.md                    # This file
```