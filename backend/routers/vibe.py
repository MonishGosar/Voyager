"""
Vibe analysis router — handles mood board photo uploads.

Accepts multipart file uploads of travel inspiration images, forwards
them to the Gemini-powered vibe analysis service, and returns a
structured VibeProfile with extracted travel signals.

Endpoints:
    POST /api/vibe — Upload 1-6 photos, receive a VibeProfile
"""

from fastapi import APIRouter, File, UploadFile
from typing import List

from models.vibe import VibeProfile
from services.gemini_service import analyze_vibe

router = APIRouter()


@router.post("/vibe", response_model=VibeProfile)
async def extract_vibe(files: List[UploadFile] = File(...)) -> VibeProfile:
    """Extract a travel vibe profile from uploaded mood board photos.

    Args:
        files: List of uploaded image files (JPEG, PNG, WEBP). Max 6.

    Returns:
        VibeProfile with tags, mood, travel_style, pace, place_signals,
        must_haves, avoid_hints, suggested_destinations, meal_style,
        and time_of_day_preference.

    Raises:
        422: If no files are provided (FastAPI validation).
    """
    image_bytes_list: list[bytes] = []
    for file in files:
        contents = await file.read()
        image_bytes_list.append(contents)

    res = analyze_vibe(image_bytes_list)
    return VibeProfile(**res)
