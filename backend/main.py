"""
TripMind Voyager — FastAPI application entry point.

Sets up the FastAPI application with CORS middleware, API routers,
health check endpoint, global exception handlers, and optional static
file serving for the Next.js frontend build.

Architecture:
    - /api/vibe  → Mood board photo analysis (Gemini multimodal)
    - /api/plan  → Itinerary generation (Gemini structured output)
    - /health    → Health check for Cloud Run readiness probes
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import os
import logging
import traceback

from routers import vibe, plan
from constants import API_PREFIX

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="TripMind Voyager API",
    description="The world's first constraint-solving, vibe-reading travel intelligence engine.",
    version="1.0.0",
)


# ──────────────────────────────────────────────
# Global Exception Handlers
# ──────────────────────────────────────────────


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle Pydantic validation errors globally.

    Args:
        request: The incoming FastAPI request.
        exc: The Pydantic ValidationError that was raised.

    Returns:
        JSONResponse with 422 status and structured error details.
    """
    logger.error(
        "Validation error on %s %s: %s",
        request.method,
        request.url.path,
        exc.error_count(),
    )
    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "detail": exc.errors(),
            "message": "Request data failed validation. Check the 'detail' field for specifics.",
        },
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """Handle ValueError exceptions globally.

    Args:
        request: The incoming FastAPI request.
        exc: The ValueError that was raised.

    Returns:
        JSONResponse with 400 status and error message.
    """
    logger.error(
        "ValueError on %s %s: %s",
        request.method,
        request.url.path,
        str(exc),
    )
    return JSONResponse(
        status_code=400,
        content={
            "error": "bad_request",
            "message": str(exc),
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler for unhandled exceptions.

    Prevents raw exception strings from leaking to the client.
    Logs the full traceback server-side for debugging.

    Args:
        request: The incoming FastAPI request.
        exc: The unhandled exception.

    Returns:
        JSONResponse with 500 status and a safe error message.
    """
    logger.error(
        "Unhandled exception on %s %s: %s\n%s",
        request.method,
        request.url.path,
        str(exc),
        traceback.format_exc(),
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "An unexpected error occurred. Please try again later.",
        },
    )


# ──────────────────────────────────────────────
# Middleware
# ──────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────
# Routers
# ──────────────────────────────────────────────

app.include_router(vibe.router, prefix=API_PREFIX)
app.include_router(plan.router, prefix=API_PREFIX)


# ──────────────────────────────────────────────
# Endpoints
# ──────────────────────────────────────────────


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint for Cloud Run readiness probes.

    Returns:
        A dict with status 'ok' indicating the service is healthy.
    """
    return {"status": "ok"}


# ──────────────────────────────────────────────
# Static File Serving (production)
# ──────────────────────────────────────────────

frontend_dir: str = os.path.join(os.path.dirname(__file__), "..", "frontend", "out")
if os.path.isdir(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="static")
