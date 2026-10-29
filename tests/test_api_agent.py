import json

import pytest
from fastapi.testclient import TestClient

from eph_agent.api import app
from eph_agent.providers import ModelTurn, ProviderRegistry, ToolCall


class FakeProvider:
    model = "fake-model"

    def __init__(self, turns: list[ModelTurn]) -> None:
        self.turns = list(turns)

    async def complete_with_tools(self, messages, tools, *, model, temperature):
        if not self.turns:
            raise AssertionError("turno inesperado")
        return self.turns.pop(0)


class AlwaysToolsProvider(FakeProvider):
    async def complete_with_tools(self, messages, tools, *, model, temperature):
        return ModelTurn(
            tool_calls=[ToolCall(id="c", name="ejecutar_sql", arguments={"query": "SELECT 1"})]
        )


@pytest.fixture()
def client(semantic_database, tmp_path, monkeypatch):
    providers = tmp_path / "providers.yml"
    providers.write_text(
        json.dumps(
            {
                "mode": "local",
                "profiles": {
                    "local": {
                        "base_url": "http://127.0.0.1:20128/v1",
                        "model": "auto",
                        "hosted": False,
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("EPH_DATABASE_BACKEND", "sqlite")
    monkeypatch.setenv("EPH_DATABASE_URL", f"sqlite:///{semantic_database}")
    monkeypatch.setenv("EPH_PROVIDERS_FILE", str(providers))
    monkeypatch.setenv("EPH_MODE", "local")
    app.state.selected_profile = None
    with TestClient(app) as test_client:
        yield test_client


def patch_provider(monkeypatch, provider) -> None:
    def fake_create(self, name, *, transport=None):
        return provider

    monkeypatch.setattr(ProviderRegistry, "create", fake_create)


def test_agent_ask_devuelve_salida_auditable(client, monkeypatch) -> None:
    provider = FakeProvider(
        [
            ModelTurn(
                tool_calls=[
                    ToolCall(
                        id="c1",
                        name="ejecutar_sql",
                        arguments={"query": "SELECT COUNT(*) AS total FROM personas"},
                    )
                ]
            ),
            ModelTurn(content=json.dumps({"answer": "Hay 43.739 personas."})),
        ]
    )
    patch_provider(monkeypatch, provider)

    response = client.post("/api/agent/ask", json={"question": "¿Cuántas personas hay?"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["result"] == {
        "kind": "scalar",
        "value": 43_739,
        "columns": ["total"],
        "rows": [[43_739]],
    }
    assert payload["profile"] == "local"
    assert payload["model"] == "fake-model"
    assert "personas" in payload["sql"]


def test_agent_ask_acota_periodo(client, monkeypatch) -> None:
    patch_provider(monkeypatch, FakeProvider([]))

    response = client.post("/api/agent/ask", json={"question": "¿Tasa de desempleo de 2025?"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["sql"] is None
    assert "1T 2026" in payload["answer"]


def test_agent_ask_falla_si_no_termina(client, monkeypatch) -> None:
    patch_provider(monkeypatch, AlwaysToolsProvider([]))

    response = client.post("/api/agent/ask", json={"question": "¿Cuántas personas hay?"})

    assert response.status_code == 502
    assert "No se devuelve una respuesta inventada" in response.json()["detail"]


def test_agent_ask_rechaza_pregunta_vacia(client) -> None:
    response = client.post("/api/agent/ask", json={"question": ""})

    assert response.status_code == 422
