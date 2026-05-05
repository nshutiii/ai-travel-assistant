import importlib

from fastapi.testclient import TestClient


def _reload_app() -> object:
    from app.core.config import get_settings

    get_settings.cache_clear()

    import app.core.database as database_module
    import app.deps as deps_module
    import app.main as main_module
    import app.models.user as user_module
    import app.routers.auth as auth_module
    import app.routers.users as users_module

    importlib.reload(database_module)
    importlib.reload(user_module)
    importlib.reload(deps_module)
    importlib.reload(auth_module)
    importlib.reload(users_module)
    importlib.reload(main_module)

    return main_module.app


def test_register_login_and_me_flow(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "auth_test.sqlite"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path.as_posix()}")

    app = _reload_app()

    with TestClient(app) as client:
        register_response = client.post(
            "/auth/register",
            json={"email": "traveler@example.com", "password": "password123"},
        )
        assert register_response.status_code == 200
        assert register_response.json()["email"] == "traveler@example.com"

        dup_response = client.post(
            "/auth/register",
            json={"email": "traveler@example.com", "password": "password456"},
        )
        assert dup_response.status_code == 409

        login_response = client.post(
            "/auth/login",
            json={"email": "traveler@example.com", "password": "password123"},
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        me_missing = client.get("/users/me")
        assert me_missing.status_code == 401

        me_ok = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
        assert me_ok.status_code == 200
        assert me_ok.json()["email"] == "traveler@example.com"


def test_login_invalid_credentials(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "auth_invalid.sqlite"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path.as_posix()}")

    app = _reload_app()

    with TestClient(app) as client:
        client.post(
            "/auth/register",
            json={"email": "alice@example.com", "password": "password123"},
        )

        bad_login = client.post(
            "/auth/login",
            json={"email": "alice@example.com", "password": "wrong-password"},
        )
        assert bad_login.status_code == 401
