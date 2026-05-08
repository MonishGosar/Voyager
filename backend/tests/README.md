# 🧪 Voyager Test Suite

Comprehensive automated test suite for the Voyager backend. All tests use mocked external services (Gemini, BigQuery, Firestore) and can run offline with a single command.

## Running Tests

```bash
cd backend
pytest
```

For verbose output with coverage:
```bash
pytest -v --tb=long
```

## Test Suites

| File | Type | What it covers |
|------|------|----------------|
| `test_constants.py` | Unit | All constants are defined, sensible defaults, prompt keywords |
| `test_cache.py` | Unit | TTL cache: set/get, expiration, eviction, invalidation, thread safety |
| `test_models.py` | Unit | Pydantic models: validation, defaults, serialization, field bounds |
| `test_gemini_service.py` | Unit | `analyze_vibe()` and `generate_itinerary()` with mocked Gemini |
| `test_google_services.py` | Unit | Firestore & BigQuery graceful fallback when GCP unavailable |
| `test_api_integration.py` | Integration | Full API endpoint tests: `/health`, `/api/vibe`, `/api/plan` |
| `test_workflow.py` | Workflow | End-to-end: upload photo → extract vibe → generate itinerary |

## Architecture

```
tests/
├── __init__.py              # Test package
├── conftest.py              # Shared fixtures (mock data, clients)
├── test_constants.py        # Constants validation
├── test_cache.py            # TTL cache unit tests
├── test_models.py           # Pydantic model tests
├── test_gemini_service.py   # Gemini service unit tests
├── test_google_services.py  # Firestore + BigQuery tests
├── test_api_integration.py  # API endpoint integration tests
└── test_workflow.py         # End-to-end workflow tests
```

## Mocking Strategy

All external services are mocked to enable fast, offline testing:

- **Gemini API**: Patched via `unittest.mock.patch("services.gemini_service.client")`
- **Firestore**: Patched via settings (`GOOGLE_CLOUD_PROJECT=""`) → graceful no-op
- **BigQuery**: Patched via settings (`GOOGLE_CLOUD_PROJECT=""`) → graceful no-op

Mock data fixtures are defined in `conftest.py` and provide realistic response shapes matching the actual Gemini output schemas.
