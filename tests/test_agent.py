import json

import pytest

from eph_agent.agent import AgentError, AgentService, detect_period_conflict
from eph_agent.answer import (
    AnswerValidationError,
    normalize_structured,
    parse_structured_answer,
    validate_agent_answer,
)
from eph_agent.database.sqlite import SQLiteAdapter
from eph_agent.providers import Message, ModelTurn, ToolCall


class FakeProvider:
    def __init__(self, turns: list[ModelTurn]) -> None:
        self.turns = list(turns)
        self.seen: list[list[Message]] = []

    async def list_models(self) -> list[str]:
        return ["fake-model"]

    async def health(self):
        raise NotImplementedError

    async def complete_with_tools(self, messages, tools, *, model, temperature):
        self.seen.append(list(messages))
        if not self.turns:
            raise AssertionError("el test pidió más turnos de los previstos")
        return self.turns.pop(0)


@pytest.fixture()
def adapter(semantic_database):
    instance = SQLiteAdapter(semantic_database)
    try:
        yield instance
    finally:
        instance.close()


def sql_call(query: str, call_id: str = "call-1") -> ToolCall:
    return ToolCall(id=call_id, name="ejecutar_sql", arguments={"query": query})


def final(answer: str, **extra) -> ModelTurn:
    payload = {"answer": answer, **extra}
    return ModelTurn(content=json.dumps(payload, ensure_ascii=False))


async def test_responde_con_valor_sql_y_supuestos(adapter) -> None:
    provider = FakeProvider(
        [
            ModelTurn(tool_calls=[sql_call("SELECT COUNT(*) AS total FROM personas")]),
            final(
                "Hay 43.739 personas en la muestra.",
                assumptions=["Se contaron personas sin ponderar."],
            ),
        ]
    )
    service = AgentService(adapter, provider, model="fake-model", profile="local")

    answer = await service.ask("¿Cuántas personas hay?")

    assert answer.result.kind == "scalar"
    assert answer.result.value == 43_739
    assert answer.sql and "personas" in answer.sql and "LIMIT" in answer.sql
    assert answer.assumptions == ["Se contaron personas sin ponderar."]
    assert answer.profile == "local"
    assert answer.model == "fake-model"
    assert answer.sample_size == 1
    assert not any("No se ejecutó" in warning for warning in answer.warnings)


async def test_reintenta_cuando_el_sql_falla(adapter) -> None:
    provider = FakeProvider(
        [
            ModelTurn(tool_calls=[sql_call("SELECT * FROM individual")]),
            ModelTurn(tool_calls=[sql_call("SELECT COUNT(*) AS total FROM personas", "call-2")]),
            final("Hay 43.739 personas."),
        ]
    )
    service = AgentService(adapter, provider, model="fake-model")

    answer = await service.ask("¿Cuántas personas hay?")

    assert answer.result.value == 43_739
    second_call = provider.seen[1]
    tool_messages = [message for message in second_call if message.role == "tool"]
    assert tool_messages and "Solo se pueden consultar las vistas" in (
        tool_messages[0].content or ""
    )


async def test_agota_los_turnos_sin_inventar(adapter) -> None:
    provider = FakeProvider(
        [
            ModelTurn(tool_calls=[sql_call("SELECT 1")]),
            ModelTurn(tool_calls=[sql_call("SELECT 2", "call-2")]),
        ]
    )
    service = AgentService(adapter, provider, model="fake-model", max_turns=2)

    with pytest.raises(AgentError, match="No se devuelve una respuesta inventada"):
        await service.ask("¿Cuántas personas hay?")


async def test_rechaza_otro_periodo_antes_de_llamar_al_modelo(adapter) -> None:
    provider = FakeProvider([])
    service = AgentService(adapter, provider, model="fake-model")

    answer = await service.ask("¿Tasa de desocupación del 2T 2025?")

    assert answer.sql is None
    assert answer.result.value is None
    assert "1T 2026" in answer.answer
    assert provider.seen == []


async def test_sin_sql_advierte_que_no_hay_respaldo(adapter) -> None:
    provider = FakeProvider([final("Hay 43.739 personas.")])
    service = AgentService(adapter, provider, model="fake-model")

    answer = await service.ask("¿Cuántas personas hay?")

    assert answer.result.value is None
    assert answer.sql is None
    assert any("No se ejecutó ninguna consulta" in warning for warning in answer.warnings)


async def test_tabla_vacia_advierte(adapter) -> None:
    provider = FakeProvider(
        [
            ModelTurn(tool_calls=[sql_call("SELECT * FROM personas WHERE 1 = 0")]),
            final("No hay filas."),
        ]
    )
    service = AgentService(adapter, provider, model="fake-model")

    answer = await service.ask("¿Hay personas?")

    assert answer.result.kind == "table"
    assert answer.result.rows == []
    assert any("no devolvió filas" in warning for warning in answer.warnings)


async def test_resultado_truncado_advierte(semantic_database) -> None:
    adapter = SQLiteAdapter(semantic_database, row_limit=5)
    provider = FakeProvider(
        [
            ModelTurn(tool_calls=[sql_call("SELECT codusu FROM personas")]),
            final("Se listaron personas."),
        ]
    )
    service = AgentService(adapter, provider, model="fake-model")
    try:
        answer = await service.ask("Listá personas")
    finally:
        adapter.close()

    assert len(answer.result.rows) == 5
    assert any("se truncó" in warning for warning in answer.warnings)


async def test_respuesta_no_estructurada_se_conserva_como_texto(adapter) -> None:
    provider = FakeProvider([ModelTurn(content="Hay 43.739 personas.")])
    service = AgentService(adapter, provider, model="fake-model")

    answer = await service.ask("¿Cuántas personas hay?")

    assert answer.answer == "Hay 43.739 personas."
    assert any("no siguió el formato estructurado" in warning for warning in answer.warnings)


def test_detecta_periodos_fuera_de_alcance() -> None:
    assert detect_period_conflict("¿Tasa del 1T 2026?") is None
    assert detect_period_conflict("¿Tasa de 2026?") is None
    assert "1T 2026" in (detect_period_conflict("¿Tasa de 2025?") or "")
    assert detect_period_conflict("¿Tasa del segundo trimestre?") is not None
    assert detect_period_conflict("¿Tasa del 3T 2026?") is not None


def test_parser_acepta_json_con_claves_en_espanol() -> None:
    raw = """```json
    {"respuesta": "ok", "supuestos": ["a"], "advertencias": [],
     "resultado": {"kind": "scalar", "value": 1}}
    ```"""

    parsed = normalize_structured(parse_structured_answer(raw))

    assert parsed["answer"] == "ok"
    assert parsed["assumptions"] == ["a"]
    assert parsed["result"] == {"kind": "scalar", "value": 1}


def test_validacion_rechaza_datos_sin_sql() -> None:
    with pytest.raises(AnswerValidationError, match="debe incluir el SQL"):
        validate_agent_answer(
            {
                "result": {"kind": "scalar", "value": 1},
                "answer": "uno",
                "profile": "local",
                "model": "m",
            }
        )


def test_validacion_rechaza_texto_vacio() -> None:
    with pytest.raises(AnswerValidationError, match="no puede estar vacía"):
        validate_agent_answer(
            {
                "result": {},
                "answer": "   ",
                "profile": "local",
                "model": "m",
            }
        )


async def test_debug_incluye_la_traza_del_loop(adapter) -> None:
    provider = FakeProvider(
        [
            ModelTurn(tool_calls=[sql_call("SELECT COUNT(*) AS total FROM personas")]),
            final("Hay 43.739 personas."),
        ]
    )
    service = AgentService(adapter, provider, model="fake-model", debug=True)

    answer = await service.ask("¿Cuántas personas hay?")

    assert answer.trace is not None
    assert len(answer.trace) == 2
    assert answer.trace[0]["tool_calls"][0]["name"] == "ejecutar_sql"
    assert answer.trace[0]["tool_results"][0]["result"]["row_count"] == 1
    assert answer.trace[1]["content"]


async def test_sin_debug_no_expone_traza(adapter) -> None:
    provider = FakeProvider([final("ok")])
    service = AgentService(adapter, provider, model="fake-model")

    answer = await service.ask("¿?")

    assert answer.trace is None
