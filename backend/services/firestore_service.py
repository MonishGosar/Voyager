"""
Google Cloud Firestore service for persisting itineraries.

Provides CRUD operations against Firestore to persist generated itineraries,
enabling users to retrieve past trips and demonstrating stateful use of
Google Cloud infrastructure beyond API-only calls.

Requires:
    - google-cloud-firestore package
    - GOOGLE_CLOUD_PROJECT env var set (or Application Default Credentials)

Falls back gracefully when Firestore is unavailable (local dev without GCP).
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import Any, Optional

from config import settings

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# Firestore client initialization
# ──────────────────────────────────────────────

_firestore_client = None


def _get_firestore_client() -> Any:
    """Lazily initialize the Firestore client.

    Returns:
        google.cloud.firestore.Client or None if unavailable.

    Side effects:
        Sets the module-level _firestore_client on first successful call.
    """
    global _firestore_client
    if _firestore_client is not None:
        return _firestore_client

    if not settings.GOOGLE_CLOUD_PROJECT:
        logger.info("GOOGLE_CLOUD_PROJECT not set — Firestore disabled.")
        return None

    try:
        from google.cloud import firestore
        _firestore_client = firestore.Client(project=settings.GOOGLE_CLOUD_PROJECT)
        logger.info("Firestore client initialized for project: %s", settings.GOOGLE_CLOUD_PROJECT)
        return _firestore_client
    except Exception as e:
        logger.warning("Firestore unavailable: %s", e)
        return None


# ──────────────────────────────────────────────
# CRUD Operations
# ──────────────────────────────────────────────

def save_itinerary(
    itinerary: dict,
    meta: dict,
    vibe: Optional[dict] = None,
) -> Optional[str]:
    """Persist a generated itinerary to Firestore.

    Args:
        itinerary: The full itinerary dict (days, stops, costs, etc.).
        meta: Trip metadata (destination, dates, group info, budget).
        vibe: Optional vibe profile from mood board analysis.

    Returns:
        The document ID string if saved successfully, or None if Firestore
        is unavailable.

    Side effects:
        Creates a document in the 'itineraries' Firestore collection.
    """
    client = _get_firestore_client()
    if client is None:
        return None

    try:
        from constants import FIRESTORE_ITINERARIES_COLLECTION, FIRESTORE_DOCUMENT_VERSION

        doc_id = str(uuid.uuid4())
        doc_data = {
            "itinerary": itinerary,
            "meta": meta,
            "vibe": vibe or {},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "version": FIRESTORE_DOCUMENT_VERSION,
        }
        client.collection(FIRESTORE_ITINERARIES_COLLECTION).document(doc_id).set(doc_data)
        logger.info("Itinerary saved to Firestore: %s", doc_id)
        return doc_id
    except Exception as e:
        logger.error("Failed to save itinerary to Firestore: %s", e)
        return None


def get_itinerary(doc_id: str) -> Optional[dict]:
    """Retrieve a persisted itinerary from Firestore by document ID.

    Args:
        doc_id: The Firestore document ID.

    Returns:
        The itinerary document dict, or None if not found or unavailable.
    """
    client = _get_firestore_client()
    if client is None:
        return None

    try:
        from constants import FIRESTORE_ITINERARIES_COLLECTION

        doc = client.collection(FIRESTORE_ITINERARIES_COLLECTION).document(doc_id).get()
        if doc.exists:
            return doc.to_dict()
        return None
    except Exception as e:
        logger.error("Failed to retrieve itinerary from Firestore: %s", e)
        return None


def list_itineraries(limit: int = 20) -> list[dict]:
    """List recent itineraries from Firestore, ordered by creation time.

    Args:
        limit: Maximum number of itineraries to return. Defaults to 20.

    Returns:
        A list of itinerary document dicts with their IDs.
    """
    client = _get_firestore_client()
    if client is None:
        return []

    try:
        from constants import FIRESTORE_ITINERARIES_COLLECTION

        docs = (
            client.collection(FIRESTORE_ITINERARIES_COLLECTION)
            .order_by("created_at", direction="DESCENDING")
            .limit(limit)
            .stream()
        )
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]
    except Exception as e:
        logger.error("Failed to list itineraries from Firestore: %s", e)
        return []
