"""
Vibe analysis router — handles mood board photo uploads.

Accepts multipart file uploads of travel inspiration images, forwards
them to the Gemini-powered vibe analysis service, and returns a
structured VibeProfile with extracted travel signals.

Endpoints:
    POST /api/vibe — Upload 1-6 photos, receive a VibeProfile
"""

from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from typing import List
import logging

from models.vibe import VibeProfile
from services.gemini_service import analyze_vibe
from constants import MAX_UPLOAD_IMAGES, MAX_IMAGE_SIZE_BYTES

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/vibe", response_model=VibeProfile)
async def extract_vibe(files: List[UploadFile] = File(...)) -> VibeProfile:
    """Extract a travel vibe profile from uploaded mood board photos.

    Validates the uploaded files for count and size limits, reads them
    into memory, and passes raw bytes to the Gemini vibe analysis service.

    Args:
        files: List of uploaded image files (JPEG, PNG, WEBP).
            Maximum of MAX_UPLOAD_IMAGES (6) files allowed.

    Returns:
        VibeProfile with tags, mood, travel_style, pace, place_signals,
        must_haves, avoid_hints, suggested_destinations, meal_style,
        and time_of_day_preference.

    Raises:
        HTTPException(400): If too many files are uploaded.
        HTTPException(413): If any single file exceeds MAX_IMAGE_SIZE_BYTES.
        HTTPException(500): If Gemini analysis fails unexpectedly.
    """
    if len(files) > MAX_UPLOAD_IMAGES:
        logger.warning(
            "extract_vibe: received %d files, max is %d",
            len(files),
            MAX_UPLOAD_IMAGES,
        )
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {MAX_UPLOAD_IMAGES} images allowed. Received {len(files)}.",
        )

    image_bytes_list: list[bytes] = []
    for idx, file in enumerate(files):
        try:
            contents: bytes = await file.read()
        except Exception as e:
            logger.error("extract_vibe: failed to read file %d (%s): %s", idx, file.filename, e)
            raise HTTPException(
                status_code=400,
                detail=f"Failed to read file '{file.filename}'.",
            )

        if len(contents) > MAX_IMAGE_SIZE_BYTES:
            logger.warning(
                "extract_vibe: file %s exceeds size limit (%d bytes > %d bytes)",
                file.filename,
                len(contents),
                MAX_IMAGE_SIZE_BYTES,
            )
            raise HTTPException(
                status_code=413,
                detail=f"File '{file.filename}' exceeds the {MAX_IMAGE_SIZE_BYTES // (1024 * 1024)}MB size limit.",
            )
        image_bytes_list.append(contents)

    try:
        res: dict = analyze_vibe(image_bytes_list)
        return VibeProfile(**res)
    except ValueError as e:
        logger.error("extract_vibe: validation error building VibeProfile: %s", e)
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error("extract_vibe: unexpected error during vibe analysis: %s", e)
        raise HTTPException(
            status_code=500,
            detail="Vibe analysis failed. Please try again.",
        )
