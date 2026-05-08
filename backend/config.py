"""
Application settings loaded from environment variables.

Uses pydantic-settings to load and validate environment variables from
the project-level .env file. All external API keys and cloud project
configuration are centralized here.

Usage:
    from config import settings
    key = settings.GEMINI_API_KEY
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application-wide settings loaded from environment variables.

    All external credentials and cloud configuration are sourced from
    the .env file at the project root. Default values are provided for
    optional settings to allow local development without full GCP setup.

    Attributes:
        GEMINI_API_KEY: API key for Google Gemini (AI Studio mode).
            Required unless GOOGLE_CLOUD_PROJECT is set (Vertex AI mode).
        GOOGLE_MAPS_API_KEY: API key for Google Maps/Places APIs.
        GOOGLE_CLOUD_PROJECT: GCP project ID. Enables Firestore, BigQuery,
            and Vertex AI mode for Gemini.
        GOOGLE_CLOUD_LOCATION: GCP region for Vertex AI and BigQuery.
    """

    GEMINI_API_KEY: str = ""
    GOOGLE_MAPS_API_KEY: str = ""
    GOOGLE_CLOUD_PROJECT: str = ""
    GOOGLE_CLOUD_LOCATION: str = "asia-south2"

    class Config:
        """Pydantic settings configuration."""

        env_file = "../.env"


settings: Settings = Settings()
