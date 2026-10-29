import pytest
from fastapi.testclient import TestClient

from eph_agent.api import app


@pytest.fixture()
def client(semantic_database, monkeypatch):
    monkeypatch.setenv("EPH_DATABASE_BACKEND", "sqlite")
    monkeypatch.setenv("EPH_DATABASE_URL", f"sqlite:///{semantic_database}")
    with TestClient(app) as test_client:
        yield test_client


def test_health_informa_backend_y_vistas(client) -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload == {
        "status": "ok",
        "backend": "sqlite",
        "dialect": "sqlite",
        "views": ["hogares", "personas"],
    }


def test_schema_lista_las_vistas(client) -> None:
    response = client.get("/api/schema")

    assert response.status_code == 200
    assert [view["view"] for view in response.json()["views"]] == ["hogares", "personas"]


def test_describe_table_devuelve_la_ficha(client) -> None:
    response = client.post("/api/tools/describe-table", json={"nombre": "personas"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["view"] == "personas"
    assert len(payload["columns"]) == 26
    sexo = next(column for column in payload["columns"] if column["column"] == "sexo")
    assert sexo["possible_values"] == ["Varón", "Mujer"]


def test_describe_table_inexistente_devuelve_404(client) -> None:
    response = client.post("/api/tools/describe-table", json={"nombre": "viviendas"})

    assert response.status_code == 404


def test_execute_sql_devuelve_resultado_y_sql(client) -> None:
    response = client.post(
        "/api/tools/execute-sql",
        json={"query": "SELECT COUNT(*) AS total FROM personas"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["columns"] == ["total"]
    assert payload["rows"] == [[43_739]]
    assert "LIMIT 1001" in payload["sql"]


@pytest.mark.parametrize(
    "query",
    [
        "SELECT * FROM individual",
        "DELETE FROM personas",
        "SELECT 1; SELECT 2",
    ],
)
def test_execute_sql_rechaza_consultas_peligrosas(client, query) -> None:
    response = client.post("/api/tools/execute-sql", json={"query": query})

    assert response.status_code == 400
    assert "detail" in response.json()
