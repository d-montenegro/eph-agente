import json

import pytest
from fastapi.testclient import TestClient

from eph_agent.api import app


def write_providers(tmp_path) -> str:
    path = tmp_path / "providers.yml"
    path.write_text(
        json.dumps(
            {
                "mode": "local",
                "allowed_hosts": ["api.permitida.test"],
                "profiles": {
                    "local": {
                        "base_url": "http://127.0.0.1:20128/v1",
                        "model": "auto",
                        "api_key_env": "LOCAL_KEY",
                        "hosted": False,
                    },
                    "remoto": {
                        "base_url": "https://api.permitida.test/v1",
                        "model": "modelo-remoto",
                        "api_key_env": "REMOTE_KEY",
                        "hosted": True,
                    },
                },
            }
        ),
        encoding="utf-8",
    )
    return str(path)


@pytest.fixture()
def client(tmp_path, monkeypatch):
    app.state.selected_profile = None
    app.state.custom_profiles = {}
    app.state.custom_keys = {}
    monkeypatch.setenv("EPH_PROVIDERS_FILE", write_providers(tmp_path))
    monkeypatch.setenv("EPH_MODE", "local")
    monkeypatch.delenv("EPH_ALLOWED_LLM_HOSTS", raising=False)
    monkeypatch.setenv("REMOTE_KEY", "clave-super-secreta")
    with TestClient(app) as test_client:
        yield test_client


def test_lista_perfiles_sin_exponer_claves(client) -> None:
    response = client.get("/api/providers")

    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "local"
    assert {profile["name"] for profile in payload["profiles"]} == {"local", "remoto"}
    assert "clave-super-secreta" not in response.text
    remoto = next(item for item in payload["profiles"] if item["name"] == "remoto")
    assert remoto["has_api_key"] is True
    assert remoto["api_key_env"] == "REMOTE_KEY"


def test_selecciona_un_perfil_en_modo_local(client) -> None:
    response = client.post("/api/providers/select", json={"profile": "local"})

    assert response.status_code == 200
    assert response.json()["name"] == "local"
    assert client.get("/api/providers").json()["selected"] == "local"


def test_rechaza_perfil_inexistente(client) -> None:
    response = client.post("/api/providers/select", json={"profile": "no-existe"})

    assert response.status_code == 400


def test_test_sin_destino_devuelve_400(client) -> None:
    response = client.post("/api/providers/test", json={})

    assert response.status_code == 400


def test_hosted_solo_lista_perfiles_permitidos(tmp_path, monkeypatch) -> None:
    app.state.selected_profile = None
    app.state.custom_profiles = {}
    app.state.custom_keys = {}
    monkeypatch.setenv("EPH_PROVIDERS_FILE", write_providers(tmp_path))
    monkeypatch.setenv("EPH_MODE", "hosted")
    monkeypatch.setenv("EPH_ALLOWED_LLM_HOSTS", "api.permitida.test")

    with TestClient(app) as hosted:
        payload = hosted.get("/api/providers").json()
        assert payload["mode"] == "hosted"
        assert [profile["name"] for profile in payload["profiles"]] == ["remoto"]
        assert hosted.post("/api/providers/select", json={"profile": "local"}).status_code == 400


def test_hosted_rechaza_base_url_arbitraria(tmp_path, monkeypatch) -> None:
    app.state.selected_profile = None
    app.state.custom_profiles = {}
    app.state.custom_keys = {}
    monkeypatch.setenv("EPH_PROVIDERS_FILE", write_providers(tmp_path))
    monkeypatch.setenv("EPH_MODE", "hosted")
    monkeypatch.setenv("EPH_ALLOWED_LLM_HOSTS", "api.permitida.test")

    with TestClient(app) as hosted:
        response = hosted.post(
            "/api/providers/test",
            json={"base_url": "http://interno.test/v1", "model": "x"},
        )

    assert response.status_code == 400
    assert "destinos arbitrarios" in response.json()["detail"]


def test_agrega_un_perfil_personalizado_en_local(client) -> None:
    response = client.post(
        "/api/providers/custom",
        json={
            "name": "mi-ollama",
            "base_url": "http://127.0.0.1:11434/v1",
            "model": "qwen2.5:7b",
            "api_key": "clave-runtime",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "mi-ollama"
    assert payload["has_api_key"] is True
    assert "clave-runtime" not in response.text
    names = {profile["name"] for profile in client.get("/api/providers").json()["profiles"]}
    assert "mi-ollama" in names


def test_rechaza_perfil_personalizado_duplicado(client) -> None:
    body = {"name": "mi-ollama", "base_url": "http://127.0.0.1:11434/v1", "model": "m"}
    assert client.post("/api/providers/custom", json=body).status_code == 200

    assert client.post("/api/providers/custom", json=body).status_code == 400


def test_hosted_no_permite_perfiles_personalizados(tmp_path, monkeypatch) -> None:
    app.state.custom_profiles = {}
    app.state.custom_keys = {}
    monkeypatch.setenv("EPH_PROVIDERS_FILE", write_providers(tmp_path))
    monkeypatch.setenv("EPH_MODE", "hosted")
    monkeypatch.setenv("EPH_ALLOWED_LLM_HOSTS", "api.permitida.test")

    with TestClient(app) as hosted:
        response = hosted.post(
            "/api/providers/custom",
            json={"name": "x", "base_url": "https://otro.test/v1", "model": "m"},
        )

    assert response.status_code == 400
    assert "modo local" in response.json()["detail"]
