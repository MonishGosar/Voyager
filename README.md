# 🧭 Voyager

**The world's first constraint-solving, vibe-reading travel intelligence engine.**

TripMind Voyager is a full-stack Next.js 14 and FastAPI application that builds a real, accessible, calendar-ready itinerary based on your uploaded vibe and exact constraints, grounded in live Google API data.

## 🏗️ Architecture
- **Frontend**: Next.js 14 (App Router) + Tailwind CSS + shadcn/ui.
- **Backend**: FastAPI (Python 3.11).
- **AI**: Gemini 2.0 Flash (via `google-generativeai`).

## ☁️ Cloud Run Deployment

This repository is optimized to be deployed to Google Cloud Run as a single container, easily staying under a $5 GCP budget. 

The `Dockerfile` handles building the Next.js static export and serving it via FastAPI.

### Steps to Deploy:

1. Enable the required APIs in GCP: Cloud Run API, Cloud Build API, Artifact Registry API.
2. Ensure you have the `gcloud` CLI installed and authenticated.
3. Deploy directly using the source:
   ```bash
   gcloud run deploy tripmind-voyager \
     --source . \
     --region us-central1 \
     --allow-unauthenticated \
     --memory 512Mi \
     --set-env-vars="GEMINI_API_KEY=your_gemini_key,GOOGLE_MAPS_API_KEY=your_maps_key"
   ```
4. You will get a Cloud Run URL!

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
uvicorn main:app --reload
```