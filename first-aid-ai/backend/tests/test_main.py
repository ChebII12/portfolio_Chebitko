from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert payload["message"] == "First Aid AI Backend is running"
    assert payload["persistence"] in ["bigquery", "in_memory"]
    assert isinstance(payload["bigquery_active"], bool)
    assert payload["bigquery_dataset"] == "first_aid_ai_module1"

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome to First Aid AI Backend" in response.json()["message"]
