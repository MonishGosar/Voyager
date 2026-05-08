import google.generativeai as genai
from backend.config import settings
import json
import typing_extensions as typing

# Initialize Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)

class Destination(typing.TypedDict):
    name: str
    country: str

class VibeProfile(typing.TypedDict):
    tags: list[str]
    suggested_destinations: list[Destination]

def analyze_vibe(images: list[bytes]) -> dict:
    if not images:
        return {"tags": [], "suggested_destinations": []}
    
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    prompt = """
    Analyze these travel inspiration photos. 
    1. Extract 3-5 aesthetic vibe tags (e.g. 'cobblestone streets', 'neon nightlife', 'minimalist nature').
    2. Suggest 3 exact global destinations (city and country) that perfectly match this exact aesthetic.
    """
    
    contents = [prompt]
    for img_bytes in images:
        contents.append({"mime_type": "image/jpeg", "data": img_bytes})
        
    try:
        response = model.generate_content(
            contents,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=VibeProfile,
                temperature=0.7,
            )
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Gemini error: {e}")
        return {"tags": ["API Error"], "suggested_destinations": [{"name": "Error", "country": str(e)}]}


def generate_itinerary(constraints: dict) -> dict:
    # MOCK implementation for now
    return {
        "days": [
            {
                "stops": [
                    {
                        "time": "09:00",
                        "name": "Historical Plaza",
                        "description": "Start the day with a walk around the plaza.",
                        "wheelchair": True,
                        "vegetarian": False,
                        "stepFree": True,
                        "cost": "Free",
                        "priceLevel": 0,
                        "streetViewUrl": "",
                        "travelToNext": {"duration": "10 min", "mode": "walk"}
                    }
                ],
                "totalCost": "€50"
            }
        ],
        "conflicts_resolved": ["Swapped stairs for step-free route"],
        "total_estimated_cost": 50.0,
        "accessibility_notes": "All venues verified for step-free access."
    }
