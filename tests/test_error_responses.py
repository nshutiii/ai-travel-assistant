import importlib

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


def test_http_errors_use_detail_string(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "errors.sqlite"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path.as_posix()}")

    app = _reload_app()

    with TestClient(app) as client:
        client.post("/auth/register", json={"email": "e1@example.com", "password": "password123"})
        dup = client.post("/auth/register", json={"email": "e1@example.com", "password": "otherpass"})
        assert dup.status_code == 409
        body = dup.json()
        assert body.keys() == {"detail"}
        assert isinstance(body["detail"], str)

        bad_login = client.post(
            "/auth/login",
            json={"email": "e1@example.com", "password": "wrong"},
        )
        assert bad_login.status_code == 401
        assert bad_login.json().keys() == {"detail"}
        assert isinstance(bad_login.json()["detail"], str)

        me = client.get("/users/me")
        assert me.status_code == 401
        assert me.json().keys() == {"detail"}
        assert isinstance(me.json()["detail"], str)

        token = _register_and_login(client, "e2@example.com")
        headers = {"Authorization": f"Bearer {token}"}
        trip = client.post(
            "/trips",
            json={"destination": "X", "days": 1, "budget": 1, "trip_style": "a"},
            headers=headers,
        )
        trip_id = trip.json()["id"]

        nf = client.get(f"/trips/{trip_id + 99}", headers=headers)
        assert nf.status_code == 404
        assert nf.json().keys() == {"detail"}
        assert isinstance(nf.json()["detail"], str)

        itin_nf = client.get(f"/itineraries/{trip_id}", headers=headers)
        assert itin_nf.status_code == 404
        assert itin_nf.json().keys() == {"detail"}


def test_validation_errors_use_detail_list(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "validation.sqlite"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path.as_posix()}")

    app = _reload_app()

    with TestClient(app) as client:
        r = client.post("/auth/register", json={"email": "not-an-email", "password": "short"})
        assert r.status_code == 422
        body = r.json()
        assert "detail" in body
        assert isinstance(body["detail"], list)
        for item in body["detail"]:
            assert "loc" in item and "msg" in item and "type" in item

        token = _register_and_login(client, "valid@example.com")
        headers = {"Authorization": f"Bearer {token}"}
        bad_trip = client.post(
            "/trips",
            json={"destination": "", "days": 0, "budget": -1, "trip_style": ""},
            headers=headers,
        )
        assert bad_trip.status_code == 422
        assert isinstance(bad_trip.json()["detail"], list)
