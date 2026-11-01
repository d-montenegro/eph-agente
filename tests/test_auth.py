from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from eph_agent.api import LOGIN_THROTTLE, app
from eph_agent.auth import (
    AuthConfigError,
    LoginThrottle,
    UserStore,
    blocked_ips,
    hash_password,
    verify_password,
)

PASSWORD = "clave-de-prueba"


def write_users(tmp_path: Path) -> Path:
    path = tmp_path / "users.yml"
    encoded = hash_password(PASSWORD)
    path.write_text(
        f'users:\n  jairo:\n    password_hash: "{encoded}"\n',
        encoding="utf-8",
    )
    return path


@pytest.fixture()
def auth_client(tmp_path, monkeypatch):
    path = write_users(tmp_path)
    monkeypatch.setenv("EPH_AUTH_ENABLED", "1")
    monkeypatch.setenv("EPH_USERS_FILE", str(path))
    monkeypatch.delenv("EPH_BLOCKED_IPS", raising=False)
    LOGIN_THROTTLE.clear()
    with TestClient(app) as client:
        yield client
    LOGIN_THROTTLE.clear()


def test_hash_y_verify_password() -> None:
    encoded = hash_password(PASSWORD)

    assert encoded.startswith("pbkdf2_sha256$")
    assert verify_password(PASSWORD, encoded) is True
    assert verify_password("otra", encoded) is False
    assert verify_password(PASSWORD, "basura") is False


def test_user_store_lee_usuarios(tmp_path) -> None:
    store = UserStore.from_env({"EPH_USERS_FILE": str(write_users(tmp_path))})

    assert store.has_user("jairo") is True
    assert store.verify("jairo", PASSWORD) is True
    assert store.verify("jairo", "incorrecta") is False
    assert store.has_user("damian") is False


def test_user_store_falla_sin_usuarios(tmp_path) -> None:
    path = tmp_path / "users.yml"
    path.write_text("users: {}\n", encoding="utf-8")

    with pytest.raises(AuthConfigError):
        UserStore.from_env({"EPH_USERS_FILE": str(path)})


def test_login_protege_las_rutas(auth_client) -> None:
    assert auth_client.get("/api/providers").status_code == 401

    bad = auth_client.post(
        "/api/auth/login",
        json={"username": "jairo", "password": "incorrecta"},
    )
    assert bad.status_code == 401

    good = auth_client.post(
        "/api/auth/login",
        json={"username": "jairo", "password": PASSWORD},
    )
    assert good.status_code == 200
    assert good.json() == {"username": "jairo"}
    assert auth_client.get("/api/auth/me").json() == {"username": "jairo"}
    assert auth_client.get("/api/providers").status_code == 200

    assert auth_client.post("/api/auth/logout").status_code == 200
    assert auth_client.get("/api/auth/me").status_code == 401
    assert auth_client.get("/api/providers").status_code == 401


def test_health_es_publico(tmp_path, monkeypatch, semantic_database) -> None:
    path = write_users(tmp_path)
    monkeypatch.setenv("EPH_AUTH_ENABLED", "1")
    monkeypatch.setenv("EPH_USERS_FILE", str(path))
    monkeypatch.setenv("EPH_DATABASE_BACKEND", "sqlite")
    monkeypatch.setenv("EPH_DATABASE_URL", f"sqlite:///{semantic_database}")
    monkeypatch.delenv("EPH_BLOCKED_IPS", raising=False)
    LOGIN_THROTTLE.clear()

    with TestClient(app) as client:
        assert client.get("/api/health").status_code == 200


def test_ip_bloqueada(tmp_path, monkeypatch) -> None:
    path = write_users(tmp_path)
    monkeypatch.setenv("EPH_AUTH_ENABLED", "1")
    monkeypatch.setenv("EPH_USERS_FILE", str(path))
    monkeypatch.setenv("EPH_BLOCKED_IPS", "testclient")
    LOGIN_THROTTLE.clear()

    with TestClient(app) as client:
        response = client.get("/api/health")

    assert response.status_code == 403
    assert response.json()["detail"] == "IP bloqueada"


def test_auth_deshabilitada_no_pide_login(monkeypatch) -> None:
    monkeypatch.setenv("EPH_AUTH_ENABLED", "0")
    monkeypatch.delenv("EPH_USERS_FILE", raising=False)
    monkeypatch.delenv("EPH_BLOCKED_IPS", raising=False)

    with TestClient(app) as client:
        assert client.get("/api/auth/me").json() == {"username": "demo"}
        assert client.get("/api/providers").status_code == 200


def test_throttle_bloquea_y_resetea() -> None:
    throttle = LoginThrottle(max_failures=2, window_seconds=60, block_seconds=60)

    throttle.record_failure("1.2.3.4")
    assert throttle.is_blocked("1.2.3.4") is False
    throttle.record_failure("1.2.3.4")
    assert throttle.is_blocked("1.2.3.4") is True

    throttle.reset("1.2.3.4")
    assert throttle.is_blocked("1.2.3.4") is False


def test_blocked_ips_lee_la_lista(monkeypatch) -> None:
    monkeypatch.setenv("EPH_BLOCKED_IPS", "10.0.0.1, 10.0.0.2")

    assert blocked_ips() == frozenset({"10.0.0.1", "10.0.0.2"})
