# 🧭 TripMind Voyager — Project Plan (v2)

> **The world's first constraint-solving, vibe-reading travel intelligence engine.**
> Next.js 14 + FastAPI + Gemini 2.0 Flash + 8 Google APIs.

---

## 🎯 One-Line Pitch

Upload your travel mood board, set your constraints — TripMind Voyager resolves every conflict and builds a real, accessible, calendar-ready itinerary grounded in live Google data.

---

## 🏗️ Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **Frontend** | Next.js 14 (App Router) | SSR, API routes, image optimization built-in |
| **UI Components** | shadcn/ui + Tailwind CSS | Clean, accessible, Google-grade component quality |
| **Backend** | FastAPI (Python 3.11) | Async, fast, Pydantic-native |
| **AI** | Gemini 2.0 Flash | Multimodal, function calling, Search grounding |
| **Deployment** | Cloud Run (single container) | FastAPI serves Next.js static export |
| **Language** | TypeScript (frontend) + Python (backend) | Type safety end-to-end |

### Why Next.js over Vite/React?
- App Router gives file-based routing with zero config — faster to build
- `next/image` handles all image optimization (matters for vibe photo upload)
- Built-in API routes can proxy small requests without touching FastAPI
- Static export (`next export`) bundles into `out/` — FastAPI serves it directly
- shadcn/ui was built for Next.js — full compatibility, zero friction

### Why shadcn/ui?
- Google Material-adjacent aesthetic: clean, minimal, professional
- Every component is copy-paste into your codebase — no external dependency
- Radix UI primitives underneath — accessibility baked in (ARIA, keyboard nav)
- Works perfectly with Tailwind — judges see polished, consistent UI
- Components: Card, Badge, Button, Tabs, Dialog, Progress, Separator, Skeleton, Toggle

---

## 🧩 Feature Architecture

### Layer 1 — Vibe Onboarding (Voyager Core)
*The wow moment — photo → vibe → destination*

- User uploads 1–6 photos via drag-and-drop zone
- Gemini 2.0 Flash Vision analyzes: aesthetic, activity type, vibe words, implied destinations
- Extracted tags shown as shadcn `Badge` components: `cobblestone streets`, `rooftop bars`, `warm evening light`
- User confirms/edits → feeds into Layer 2

### Layer 2 — Constraint Input (TripMind Core)
*shadcn form components — clean, minimal, Google-like*

- Destination (or "suggest based on vibe") — shadcn `Combobox`
- Date range — shadcn `Calendar` + `Popover`
- Budget — shadcn `Input` with currency toggle
- Group profile — shadcn `ToggleGroup`
- Accessibility needs — shadcn `Checkbox` group
- Travel style — shadcn `Slider`
- Must-haves / exclusions — shadcn `Badge` input (tag input pattern)

### Layer 3 — AI Planning Engine

```
Vibe Tags + Constraints
    → FastAPI /api/plan
        → Gemini 2.0 Flash (function calling + Search grounding)
            → resolve_conflicts()
            → suggest_destination()
            → generate_day_plan()
            → enrich_with_places()       # Google Places API
            → calculate_routes()         # Google Directions API
            → check_accessibility()
        → Structured Itinerary JSON
    → Next.js renders itinerary
```

### Layer 4 — Rich Output
- **Map View**: Google Maps JS API with dark/light theme toggle, route polylines
- **Street View**: Embedded Street View preview per stop (shadcn `Dialog` on expand)
- **Day Cards**: shadcn `Card` with `Badge` for accessibility, `Separator` between stops
- **Conflict Log**: shadcn `Alert` component — amber/warning variant — shows AI reasoning
- **Export**: shadcn `Button` → Google Calendar API, copy link, PDF

### Layer 5 — Disruption + Memory
- **Disruption Handler**: shadcn `Dialog` — user describes change → Gemini re-plans affected days
- **Post-Trip Journal**: upload photos → Gemini narrative + Geocoding API → Google Drive export

---

## 📁 Repository Structure

```
tripmind-voyager/
├── README.md
├── .env.example
├── .gitignore
├── Dockerfile                        # single container for Cloud Run
├── cloudbuild.yaml                   # Cloud Build config
│
├── backend/
│   ├── main.py                       # FastAPI app — serves API + Next.js static
│   ├── requirements.txt
│   ├── config.py
│   ├── routers/
│   │   ├── vibe.py                   # POST /api/vibe
│   │   ├── plan.py                   # POST /api/plan
│   │   ├── places.py                 # GET /api/places
│   │   ├── export.py                 # POST /api/export/calendar
│   │   └── journal.py                # POST /api/journal
│   ├── services/
│   │   ├── gemini_service.py
│   │   ├── maps_service.py
│   │   ├── calendar_service.py
│   │   └── geocoding_service.py
│   ├── models/
│   │   ├── vibe.py
│   │   ├── itinerary.py
│   │   └── constraints.py
│   └── tests/
│       ├── test_vibe.py
│       ├── test_plan.py
│       ├── test_places.py
│       └── conftest.py
│
├── frontend/                         # Next.js 14 App Router
│   ├── package.json
│   ├── next.config.ts                # output: 'export' for static build
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── components.json               # shadcn/ui config
│   └── src/
│       ├── app/
│       │   ├── layout.tsx            # root layout (font, theme)
│       │   ├── page.tsx              # landing / step 1 (VibeBoard)
│       │   ├── plan/
│       │   │   └── page.tsx          # step 2 (ConstraintForm)
│       │   └── itinerary/
│       │       └── page.tsx          # step 3 (ItineraryView)
│       ├── components/
│       │   ├── vibe/
│       │   │   ├── VibeBoard.tsx
│       │   │   └── VibeTags.tsx
│       │   ├── plan/
│       │   │   ├── ConstraintForm.tsx
│       │   │   ├── sections/
│       │   │   │   ├── WhereWhen.tsx
│       │   │   │   ├── GroupProfile.tsx
│       │   │   │   ├── Preferences.tsx
│       │   │   │   └── AccessibilityNeeds.tsx
│       │   ├── itinerary/
│       │   │   ├── ItineraryView.tsx
│       │   │   ├── DayCard.tsx
│       │   │   ├── VenueCard.tsx
│       │   │   ├── ConflictLog.tsx
│       │   │   └── StreetViewModal.tsx
│       │   ├── map/
│       │   │   ├── MapView.tsx
│       │   │   └── mapStyles.ts
│       │   └── shared/
│       │       ├── AccessibilityBadge.tsx
│       │       ├── LoadingSteps.tsx
│       │       └── ExportPanel.tsx
│       ├── hooks/
│       │   ├── useVibe.ts
│       │   ├── usePlanning.ts
│       │   └── useGoogleMaps.ts
│       ├── lib/
│       │   ├── api.ts               # typed fetch wrappers
│       │   ├── utils.ts             # shadcn cn() utility
│       │   └── formatters.ts
│       └── types/
│           └── index.ts
│
└── docs/
    ├── PLAN.md
    └── DESIGN.md
```

**Estimated committed repo size: ~800 KB** (well under 10 MB)

---

## ☁️ Cloud Run Deployment

### Single-container strategy (saves credits)
FastAPI serves both the API and the Next.js static export from the same container.

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Build Next.js frontend
RUN apt-get update && apt-get install -y nodejs npm
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build        # outputs to /app/frontend/out/

# Install Python deps
WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install -r requirements.txt

# Copy backend
COPY backend/ ./backend/

# FastAPI serves static files from /app/frontend/out
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

```python
# backend/main.py — serving static Next.js build
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

# API routes first
app.include_router(vibe_router, prefix="/api")
app.include_router(plan_router, prefix="/api")
# ... other routers

# Serve Next.js static export
app.mount("/", StaticFiles(directory="frontend/out", html=True), name="static")
```

### Deploy commands
```bash
# One-time setup
gcloud run deploy tripmind-voyager \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --set-env-vars GEMINI_API_KEY=$GEMINI_API_KEY,GOOGLE_MAPS_API_KEY=$GOOGLE_MAPS_API_KEY

# Subsequent deploys
gcloud run deploy tripmind-voyager --source .
```

### Cost estimate with $5 credits
- Cloud Run: ~$0.40/million requests + $0.00002/vCPU-second
- For a hackathon demo: estimated **< $0.50 total** — well within $5 budget
- Memory: 512 Mi is sufficient; scale to 0 when idle (no idle cost)

---

## 🗺️ Google APIs — 8 Integrations

| API | Usage | Integration Point |
|-----|-------|------------------|
| **Gemini 2.0 Flash** | Vision + text + function calling | `google-generativeai` Python SDK |
| **Google Search Grounding** | Real-time data via Gemini tool | Gemini API built-in tool |
| **Maps JavaScript API** | Interactive route map | `@googlemaps/js-api-loader` in Next.js |
| **Places API (New)** | Venues, ratings, hours, accessibility | FastAPI → `places.googleapis.com` |
| **Directions API** | Routes, travel times | FastAPI → `maps.googleapis.com/directions` |
| **Street View Static API** | Destination previews | Static URL, `next/image` optimized |
| **Geocoding API** | Photo geotagging (journal) | FastAPI → `maps.googleapis.com/geocode` |
| **Google Calendar API** | One-click itinerary export | `google-api-python-client` |

---

## 🤖 AI Model: `gemini-2.0-flash`

- 1500 requests/day free tier
- Multimodal: image + text in one request
- Native function calling → structured JSON itinerary output
- Google Search grounding → real-time closures, events, warnings
- Response time < 3s for demo smoothness

```python
# Function calling schema
tools = [
    {
        "function_declarations": [
            {
                "name": "generate_itinerary",
                "description": "Generate a day-by-day travel itinerary resolving all constraints",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "days": {"type": "array", "items": {"$ref": "#/DayPlan"}},
                        "conflicts_resolved": {"type": "array", "items": {"type": "string"}},
                        "total_estimated_cost": {"type": "number"},
                        "accessibility_notes": {"type": "string"}
                    }
                }
            }
        ]
    }
]
```

---

## 📋 Build Sequence

### Phase 1 — Project Setup (Hours 1–2)
- [ ] `create-next-app` with TypeScript + Tailwind
- [ ] `npx shadcn@latest init` — configure components.json
- [ ] Install core shadcn components: `card badge button tabs dialog progress separator skeleton toggle calendar popover slider`
- [ ] FastAPI skeleton + `/health` endpoint
- [ ] `.env.example`, `.gitignore`, folder structure

### Phase 2 — Vibe Engine (Hours 2–5)
- [ ] VibeBoard component (drag-drop with shadcn styling)
- [ ] `POST /api/vibe` FastAPI route
- [ ] Gemini Vision → vibe tag extraction (structured JSON)
- [ ] VibeTags component with shadcn `Badge`
- [ ] Unit tests (mocked Gemini)

### Phase 3 — Planning Engine (Hours 5–11)
- [ ] ConstraintForm with all 4 shadcn sections
- [ ] `POST /api/plan` — Gemini function calling pipeline
- [ ] Google Places enrichment per stop
- [ ] Directions API for routes + times
- [ ] Accessibility filtering + conflict resolution log

### Phase 4 — Itinerary Output (Hours 11–17)
- [ ] ItineraryView with shadcn Card + Separator
- [ ] ConflictLog with shadcn Alert (amber variant)
- [ ] MapView — Google Maps + route polylines
- [ ] StreetViewModal — shadcn Dialog with Street View iframe
- [ ] AccessibilityBadge component

### Phase 5 — Export + Cloud Run (Hours 17–22)
- [ ] ExportPanel — Google Calendar API
- [ ] Disruption re-planning Dialog
- [ ] Dockerfile + `next.config.ts` static export
- [ ] Cloud Run deploy + test URL
- [ ] Accessibility audit (WCAG AA)

### Phase 6 — Polish + Submit (Hours 22–24)
- [ ] Test coverage check (70%+ on services)
- [ ] README finalized
- [ ] Repo size < 10 MB verified
- [ ] Single branch, public repo confirmed

---

## 🧪 Testing

**Backend (pytest + httpx):**
```
test_vibe.py    — mock Gemini Vision, assert VibeProfile structure
test_plan.py    — constraint solver, conflict detection, itinerary shape
test_places.py  — mock Places API, enrichment logic
conftest.py     — mock Gemini client, mock Maps client
```

**Frontend (Jest + React Testing Library, built into Next.js):**
```
VibeBoard.test.tsx      — drag-drop, file validation, tag render
ConstraintForm.test.tsx — form validation, accessibility field render
lib/utils.test.ts       — formatters, cost calculator
```

---

## 🔐 Security

- [ ] All API keys in `.env`, never in code
- [ ] `.env` in `.gitignore` — check with `git log --all -- .env`
- [ ] `.env.example` with placeholder values
- [ ] FastAPI proxies all Google API calls (no keys in Next.js bundle)
- [ ] Next.js env: only `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY` exposed to client (Maps JS only)
- [ ] Pydantic validation on all request bodies
- [ ] Image upload: MIME type + 5 MB max validation
- [ ] CORS: restricted to Cloud Run URL in production
- [ ] Cloud Run: `--no-allow-unauthenticated` for sensitive endpoints if needed

---

## ♿ Accessibility

shadcn/ui gives Radix UI primitives — most ARIA handled automatically. Additional checks:

- [ ] Color contrast ≥ 4.5:1 (Tailwind default palette passes)
- [ ] All images: `alt` props on every `next/image`
- [ ] Keyboard nav: Tab / Enter / Escape on all interactive elements
- [ ] Accessibility filter section always visible in ConstraintForm (never hidden)
- [ ] Venue cards: accessibility badges (`♿ Accessible`, `🌿 Veg`) with text + icon
- [ ] `prefers-reduced-motion` respected in Tailwind animations
- [ ] Focus ring visible: Tailwind `focus-visible:ring-2`

---

## 📊 Repo Size Budget

| What | Size | Committed? |
|------|------|-----------|
| Next.js source (TSX) | ~600 KB | ✅ |
| Backend source (Python) | ~150 KB | ✅ |
| Docs + README | ~60 KB | ✅ |
| Dockerfile + configs | ~5 KB | ✅ |
| `node_modules/` | ~400 MB | ❌ gitignored |
| `.next/` build cache | ~50 MB | ❌ gitignored |
| `.venv/` | ~50 MB | ❌ gitignored |
| **Total committed** | **~815 KB** | ✅ Safe |

---

## 🏆 Winning Differentiators

| Criterion | Advantage |
|-----------|-----------|
| **Code Quality** | Next.js App Router + shadcn/ui = clean, consistent, production-grade |
| **Security** | All secrets server-side, Pydantic validation, CORS locked |
| **Efficiency** | Gemini Flash, Next.js static export, Cloud Run scale-to-zero |
| **Testing** | pytest + Jest/RTL, 70%+ coverage, all APIs mocked |
| **Accessibility** | Radix UI primitives (shadcn) + built-in AI accessibility filtering |
| **Google Services** | 8 integrations — all demo-able, none superficial |

Submssion to be reviewed by AI 

**What no other team will have:**
1. Photo → vibe → itinerary (multimodal Gemini entry)
2. Constraint conflict resolution with transparent reasoning log
3. Accessibility as first-class AI constraint, not UI decoration
4. shadcn/ui quality — will look the most professional in the room
5. Cloud Run URL + single Dockerfile — clean, reproducible deployment