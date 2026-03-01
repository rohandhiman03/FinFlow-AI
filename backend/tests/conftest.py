import pytest
from fastapi.testclient import TestClient

from app.db import Base, engine
from app.main import app


@pytest.fixture()
def client() -> TestClient:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def complete_onboarding(client: TestClient):
    def _run(user_id: str) -> None:
        start = client.post(
            "/api/v1/onboarding/start",
            headers={"X-User-Id": user_id},
            json={"reset_existing": True},
        )
        session_id = start.json()["session_id"]

        sequence = [
            "Salary 5000 monthly",
            "Rent 1800, phone 80, internet 60",
            "Groceries 600, dining 300, transport 200",
            "Emergency fund 10000",
            "confirm",
        ]

        for msg in sequence:
            response = client.post(
                "/api/v1/onboarding/message",
                headers={"X-User-Id": user_id},
                json={"session_id": session_id, "message": msg},
            )
            assert response.status_code == 200

    return _run
