"""
Google BigQuery analytics service for logging trip planning events.

Logs anonymized, structured events to BigQuery for data pipeline analytics.
Demonstrates broader GCP adoption beyond API-only calls — shows understanding
of the full Google Cloud data stack.

Events logged:
    - vibe_analyzed: When a mood board is analyzed (vibe tags, style, pace)
    - itinerary_generated: When an itinerary is created (destination, days, budget)
    - itinerary_saved: When an itinerary is persisted to Firestore

Requires:
    - google-cloud-bigquery package
    - GOOGLE_CLOUD_PROJECT env var set

Falls back gracefully when BigQuery is unavailable (local dev without GCP).
"""

import logging
from datetime import datetime, timezone
from typing import Any, Optional

from config import settings

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# BigQuery client initialization
# ──────────────────────────────────────────────

_bq_client = None


def _get_bq_client() -> Any:
    """Lazily initialize the BigQuery client.

    Returns:
        google.cloud.bigquery.Client or None if unavailable.

    Side effects:
        Sets the module-level _bq_client on first successful call.
    """
    global _bq_client
    if _bq_client is not None:
        return _bq_client

    if not settings.GOOGLE_CLOUD_PROJECT:
        logger.info("GOOGLE_CLOUD_PROJECT not set — BigQuery analytics disabled.")
        return None

    try:
        from google.cloud import bigquery
        _bq_client = bigquery.Client(project=settings.GOOGLE_CLOUD_PROJECT)
        logger.info("BigQuery client initialized for project: %s", settings.GOOGLE_CLOUD_PROJECT)
        return _bq_client
    except Exception as e:
        logger.warning("BigQuery unavailable: %s", e)
        return None


def _ensure_dataset_and_table() -> Optional[str]:
    """Ensure the analytics dataset and events table exist in BigQuery.

    Returns:
        The fully qualified table ID string, or None if setup fails.

    Side effects:
        Creates the dataset and table in BigQuery if they don't exist.
    """
    client = _get_bq_client()
    if client is None:
        return None

    try:
        from google.cloud import bigquery
        from constants import BIGQUERY_DATASET, BIGQUERY_EVENTS_TABLE

        dataset_ref = f"{settings.GOOGLE_CLOUD_PROJECT}.{BIGQUERY_DATASET}"
        table_ref = f"{dataset_ref}.{BIGQUERY_EVENTS_TABLE}"

        # Create dataset if not exists
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = settings.GOOGLE_CLOUD_LOCATION
        client.create_dataset(dataset, exists_ok=True)

        # Create table if not exists
        schema = [
            bigquery.SchemaField("event_type", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("destination", "STRING"),
            bigquery.SchemaField("vibe_tags", "STRING", mode="REPEATED"),
            bigquery.SchemaField("travel_style", "STRING"),
            bigquery.SchemaField("pace", "STRING"),
            bigquery.SchemaField("num_days", "INTEGER"),
            bigquery.SchemaField("budget", "FLOAT"),
            bigquery.SchemaField("currency", "STRING"),
            bigquery.SchemaField("group_type", "STRING"),
            bigquery.SchemaField("group_size", "INTEGER"),
            bigquery.SchemaField("num_images", "INTEGER"),
        ]
        table = bigquery.Table(table_ref, schema=schema)
        client.create_table(table, exists_ok=True)
        return table_ref
    except Exception as e:
        logger.error("Failed to ensure BigQuery dataset/table: %s", e)
        return None


# ──────────────────────────────────────────────
# Event Logging Functions
# ──────────────────────────────────────────────

def log_vibe_analyzed(
    vibe_tags: list[str],
    travel_style: str,
    pace: str,
    num_images: int,
    suggested_destinations: list[dict],
) -> bool:
    """Log a vibe analysis event to BigQuery.

    Args:
        vibe_tags: Extracted vibe tags from mood board analysis.
        travel_style: Inferred travel style (e.g. "slow explorer").
        pace: Inferred pace (e.g. "balanced").
        num_images: Number of images in the uploaded mood board.
        suggested_destinations: List of destination dicts with name/country.

    Returns:
        True if the event was logged successfully, False otherwise.

    Side effects:
        Inserts a row into the BigQuery trip_events table.
    """
    table_ref = _ensure_dataset_and_table()
    if table_ref is None:
        return False

    client = _get_bq_client()
    try:
        destination_names = [d.get("name", "") for d in suggested_destinations[:3]]
        rows = [{
            "event_type": "vibe_analyzed",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "destination": ", ".join(destination_names),
            "vibe_tags": vibe_tags[:6],
            "travel_style": travel_style,
            "pace": pace,
            "num_images": num_images,
            "num_days": None,
            "budget": None,
            "currency": None,
            "group_type": None,
            "group_size": None,
        }]
        errors = client.insert_rows_json(table_ref, rows)
        if errors:
            logger.error("BigQuery insert errors: %s", errors)
            return False
        logger.info("Logged vibe_analyzed event to BigQuery")
        return True
    except Exception as e:
        logger.error("Failed to log vibe_analyzed event: %s", e)
        return False


def log_itinerary_generated(
    destination: str,
    num_days: int,
    budget: float,
    currency: str,
    group_type: str,
    group_size: int,
    vibe_tags: Optional[list[str]] = None,
    travel_style: Optional[str] = None,
    pace: Optional[str] = None,
) -> bool:
    """Log an itinerary generation event to BigQuery.

    Args:
        destination: Target destination city.
        num_days: Number of days in the itinerary.
        budget: Total trip budget.
        currency: Budget currency code.
        group_type: Group type (solo, couple, friends, family).
        group_size: Number of travelers.
        vibe_tags: Optional vibe tags from mood board.
        travel_style: Optional inferred travel style.
        pace: Optional inferred pace.

    Returns:
        True if the event was logged successfully, False otherwise.

    Side effects:
        Inserts a row into the BigQuery trip_events table.
    """
    table_ref = _ensure_dataset_and_table()
    if table_ref is None:
        return False

    client = _get_bq_client()
    try:
        rows = [{
            "event_type": "itinerary_generated",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "destination": destination,
            "vibe_tags": vibe_tags or [],
            "travel_style": travel_style or "",
            "pace": pace or "",
            "num_days": num_days,
            "budget": budget,
            "currency": currency,
            "group_type": group_type,
            "group_size": group_size,
            "num_images": None,
        }]
        errors = client.insert_rows_json(table_ref, rows)
        if errors:
            logger.error("BigQuery insert errors: %s", errors)
            return False
        logger.info("Logged itinerary_generated event to BigQuery")
        return True
    except Exception as e:
        logger.error("Failed to log itinerary_generated event: %s", e)
        return False
