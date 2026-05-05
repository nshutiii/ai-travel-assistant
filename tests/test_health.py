from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_app_starts() -> None:
    assert app.title == "AI Travel Assistant"


def test_health_check_returns_200() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
