"""
TripMind Voyager — FastAPI application entry point.

Sets up the FastAPI application with CORS middleware, API routers,
health check endpoint, and optional static file serving for the
Next.js frontend build.

Architecture:
    - /api/vibe  → Mood board photo analysis (Gemini multimodal)
    - /api/plan  → Itinerary generation (Gemini structured output)
    - /health    → Health check for Cloud Run readiness probes
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic_settings import BaseSettings
import os
import logging

from routers import vibe, plan
from constants import API_PREFIX

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Attributes:
        GEMINI_API_KEY: API key for Google Gemini (AI Studio mode).
        GOOGLE_MAPS_API_KEY: API key for Google Maps/Places APIs.
    """
    GEMINI_API_KEY: str = ""
    GOOGLE_MAPS_API_KEY: str = ""

    class Config:
        env_file = ".env"


settings = Settings()

app = FastAPI(
    title="TripMind Voyager API",
    description="The world's first constraint-solving, vibe-reading travel intelligence engine.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(vibe.router, prefix=API_PREFIX)
app.include_router(plan.router, prefix=API_PREFIX)


@app.get("/health")
def health_check() -> dict:
    """Health check endpoint for Cloud Run readiness probes.

    Returns:
        A dict with status 'ok' indicating the service is healthy.
    """
    return {"status": "ok"}


# Serve Next.js static export
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend", "out")
if os.path.isdir(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="static")
