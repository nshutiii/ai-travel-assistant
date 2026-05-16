import importlib
import logging

from fastapi.testclient import TestClient


def _reload_app() -> object:
    from app.core.config import get_settings

    get_settings.cache_clear()

    import app.core.database as database_module
    import app.deps as deps_module
    import app.main as main_module
    import app.models.itinerary as itinerary_module
    import app.models.trip as trip_module
    import app.models.user as user_module
    import app.routers.auth as auth_module
    import app.routers.itineraries as itineraries_module
    import app.routers.trips as trips_module
    import app.routers.users as users_module
    import app.services.audit_log as audit_module

    importlib.reload(database_module)
    importlib.reload(audit_module)
    importlib.reload(user_module)
    importlib.reload(trip_module)
    importlib.reload(itinerary_module)
    importlib.reload(deps_module)
    importlib.reload(auth_module)
    importlib.reload(trips_module)
    importlib.reload(itineraries_module)
    importlib.reload(users_module)
    importlib.reload(main_module)

    return main_module.app


def _register_and_login(client: TestClient, email: str) -> str:
    client.post("/auth/register", json={"email": email, "password": "password123"})
    response = client.post("/auth/login", json={"email": email, "password": "password123"})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_background_audit_after_trip_create(tmp_path, monkeypatch, caplog) -> None:
    db_path = tmp_path / "bg_trip.sqlite"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path.as_posix()}")

    app = _reload_app()

    with caplog.at_level(logging.INFO, logger="app.audit"):
        with TestClient(app) as client:
            token = _register_and_login(client, "auditor_trip@example.com")
            headers = {"Authorization": f"Bearer {token}"}
            response = client.post(
                "/trips",
                json={"destination": "Lyon", "days": 2, "budget": 400, "trip_style": "budget"},
                headers=headers,
            )
            assert response.status_code == 200
            trip_id = response.json()["id"]

    assert any("audit.trip_created" in r.message for r in caplog.records)
    assert any(str(trip_id) in r.message and "Lyon" in r.message for r in caplog.records)


def test_background_audit_after_itinerary_save(tmp_path, monkeypatch, caplog) -> None:
    db_path = tmp_path / "bg_itin.sqlite"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path.as_posix()}")

    app = _reload_app()

    with caplog.at_level(logging.INFO, logger="app.audit"):
        with TestClient(app) as client:
            token = _register_and_login(client, "auditor_itin@example.com")
            headers = {"Authorization": f"Bearer {token}"}
            trip = client.post(
                "/trips",
                json={"destination": "Nice", "days": 3, "budget": 600, "trip_style": "relax"},
                headers=headers,
            )
            trip_id = trip.json()["id"]
            client.post(
                "/itineraries",
                json={
                    "trip_id": trip_id,
                    "days": [{"day": 1, "activities": ["Promenade"]}],
                },
                headers=headers,
            )

    assert any("audit.itinerary_saved" in r.message for r in caplog.records)
    assert any(str(trip_id) in r.message and "day_count=1" in r.message for r in caplog.records)
