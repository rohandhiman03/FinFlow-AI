from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_returns_ok() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "ai_provider" in body


def test_providers_returns_supported_values() -> None:
    response = client.get("/api/v1/ai/providers")
    assert response.status_code == 200
    body = response.json()
    assert set(body["supported_providers"]) == {"claude", "gemini", "grok"}
    assert body["active_provider"] in body["supported_providers"]
