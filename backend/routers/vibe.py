from fastapi import APIRouter, File, UploadFile
from typing import List
from backend.models.vibe import VibeProfile
from backend.services.gemini_service import analyze_vibe

router = APIRouter()

@router.post("/vibe", response_model=VibeProfile)
async def extract_vibe(files: List[UploadFile] = File(...)):
    image_bytes_list = []
    for file in files:
        contents = await file.read()
        image_bytes_list.append(contents)
        
    res = analyze_vibe(image_bytes_list)
    return VibeProfile(**res)
