from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_vibe_endpoint_validation():
    # Test that hitting the endpoint without files returns a validation error
    response = client.post("/api/vibe")
    assert response.status_code == 422
