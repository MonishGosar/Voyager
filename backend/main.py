from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic_settings import BaseSettings
import os
from routers import vibe, plan

class Settings(BaseSettings):
    GEMINI_API_KEY: str = ""
    GOOGLE_MAPS_API_KEY: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings()

app = FastAPI(title="TripMind Voyager API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(vibe.router, prefix="/api")
app.include_router(plan.router, prefix="/api")

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Serve Next.js static export
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend", "out")
if os.path.isdir(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="static")


