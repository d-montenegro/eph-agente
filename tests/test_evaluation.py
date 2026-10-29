import json
from pathlib import Path

import pytest

from eph_agent.evaluation import (
    EvaluationError,
    compare_result,
    compare_runs,
    inspect_sql,
    load_cases,
    load_run,
    run_case,
    run_suite,
    save_run,
)

RAIZ = Path(__file__).resolve().parents[1]


def case_numero(actual, expected=0.0783, unidad="fraccion", tolerance=0.001):
    return compare_result(
        {"result": {"kind": "scalar", "value": actual}},
        {
            "tipo": "numero",
            "valor_esperado": expected,
            "unidad": unidad,
            "tolerancia": tolerance,
        },
    )


def test_carga_el_golden_set_visible() -> None:
    cases = load_cases(RAIZ / "eval" / "golden.yml")
    reserve = load_cases(RAIZ / "eval" / "reserve.yml")

    assert len(cases) == 16
    assert len(reserve) == 4
    assert {case["categoria"] for case in cases} >= {
        "tasas_laborales",
        "demografia",
        "ingresos",
        "trampas",
    }


def test_rechaza_caso_con_tipo_desconocido(tmp_path) -> None:
    path = tmp_path / "mal.yml"
    path.write_text(
        json.dumps(
            {
                "casos": [
                    {
                        "id": "x",
                        "pregunta": "?",
                        "tipo": "otro",
                        "categoria": "c",
                        "dificultad": "baja",
                        "fuente": "f",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(EvaluationError, match="tipo"):
        load_cases(path)


def test_compara_fraccion_con_porcentaje() -> None:
    assert case_numero(7.83)["ok"] is True


def test_compara_porcentaje_con_fraccion() -> None:
    assert case_numero(0.0783, expected=7.83, unidad="porcentaje")["ok"] is True


def test_falla_fuera_de_tolerancia() -> None:
    result = case_numero(0.09, tolerance=0.001)

    assert result["ok"] is False
    assert "tol" in result["detail"]


def test_compara_tablas_sin_importar_el_orden() -> None:
    expected = {
        "tipo": "tabla",
        "tolerancia": 0.001,
        "columns": ["sexo", "tasa"],
        "rows": [["Mujer", 0.0827], ["Varón", 0.0747]],
    }
    actual = {
        "result": {
            "kind": "table",
            "columns": ["sexo", "tasa"],
            "rows": [["Varón", 0.07472], ["Mujer", 0.08269]],
        }
    }

    assert compare_result(actual, expected)["ok"] is True


def test_tabla_con_columnas_distintas_falla() -> None:
    expected = {
        "tipo": "tabla",
        "columns": ["sexo", "tasa"],
        "rows": [],
    }

    result = compare_result(
        {"result": {"kind": "table", "columns": ["sexo"], "rows": []}}, expected
    )

    assert result["ok"] is False


def test_rechazo_exige_sql_nulo_y_mencion_del_periodo() -> None:
    expected = {"tipo": "rechazo"}
    ok = compare_result({"sql": None, "answer": "Los datos cubren solo el 1T 2026."}, expected)
    fail = compare_result({"sql": "SELECT 1", "answer": "1T 2026"}, expected)

    assert ok["ok"] is True
    assert fail["ok"] is False


def test_sin_datos_falla_si_inventa_un_valor() -> None:
    assert compare_result({"result": {"kind": "scalar", "value": None}}, {"tipo": "sin_datos"})[
        "ok"
    ]
    assert not compare_result({"result": {"kind": "scalar", "value": 0.05}}, {"tipo": "sin_datos"})[
        "ok"
    ]


def test_inspect_sql_acepta_consulta_valida() -> None:
    sql = "SELECT SUM(pondera) FROM personas WHERE estado_actividad = 'Desocupado'"

    assert (
        inspect_sql(sql, {"vistas": ["personas"], "columnas": ["pondera"], "texto": ["Desocupado"]})
        == []
    )


def test_inspect_sql_detecta_vistas_columnas_y_filtros() -> None:
    violations = inspect_sql(
        "SELECT COUNT(*) FROM individual",
        {"vistas": ["personas"], "columnas": ["pondera"], "texto": ["Desocupado"]},
    )

    joined = " ".join(violations)
    assert "vistas no esperadas" in joined
    assert "falta la columna pondera" in joined
    assert "falta el filtro" in joined


def test_run_case_registra_cada_repeticion() -> None:
    calls = {"n": 0}

    async def ask(_question):
        calls["n"] += 1
        return {
            "result": {"kind": "scalar", "value": 0.0783},
            "sql": "SELECT SUM(pondera) FROM personas WHERE estado_actividad = 'Desocupado'",
            "answer": "ok",
        }

    case = {
        "id": "x",
        "categoria": "tasas_laborales",
        "dificultad": "baja",
        "tipo": "numero",
        "pregunta": "¿?",
        "valor_esperado": 0.0783,
        "unidad": "fraccion",
        "tolerancia": 0.001,
        "reglas_sql": {"vistas": ["personas"], "columnas": ["pondera"], "texto": ["Desocupado"]},
    }

    result = __import__("asyncio").run(run_case(case, ask, repetitions=3))

    assert calls["n"] == 3
    assert result["passed"] is True
    assert result["pass_rate"] == 1.0
    assert len(result["attempts"]) == 3


def test_run_case_marca_fallo_si_la_herramienta_explota() -> None:
    async def ask(_question):
        raise RuntimeError("sin proveedor")

    case = {
        "id": "x",
        "categoria": "c",
        "dificultad": "baja",
        "tipo": "numero",
        "pregunta": "?",
        "valor_esperado": 1,
        "unidad": "absoluta",
        "tolerancia": 0,
    }

    result = __import__("asyncio").run(run_case(case, ask, repetitions=1))

    assert result["passed"] is False
    assert "RuntimeError" in result["attempts"][0]["error"]


def test_run_suite_resume_aprobados() -> None:
    async def ask(_question):
        return {"result": {"kind": "scalar", "value": 1}, "sql": "SELECT 1", "answer": "ok"}

    cases = [
        {
            "id": f"c{i}",
            "categoria": "c",
            "dificultad": "baja",
            "tipo": "numero",
            "pregunta": "?",
            "valor_esperado": 1,
            "unidad": "absoluta",
            "tolerancia": 0,
        }
        for i in range(2)
    ]

    result = __import__("asyncio").run(run_suite(cases, ask, repetitions=1))

    assert result["summary"] == {
        "total": 2,
        "passed": 2,
        "pass_rate": 1.0,
        "repetitions": 1,
    }


def test_guarda_y_lee_una_corrida(tmp_path) -> None:
    result = {"summary": {"total": 1, "passed": 1}, "cases": [{"id": "x"}]}

    path = save_run(result, tmp_path, profile="local", model="m", commit="abc123")
    loaded = load_run(path)

    assert loaded["commit"] == "abc123"
    assert loaded["profile"] == "local"
    assert loaded["model"] == "m"
    assert loaded["fecha"]
    assert path.parent == tmp_path


def test_compara_corridas_detecta_correcciones_y_regresiones() -> None:
    previous = {
        "cases": [
            {"id": "a", "passed": False, "pass_rate": 0.0},
            {"id": "b", "passed": True, "pass_rate": 1.0},
            {"id": "c", "passed": True, "pass_rate": 1.0},
        ]
    }
    current = {
        "cases": [
            {"id": "a", "passed": True, "pass_rate": 1.0},
            {"id": "b", "passed": False, "pass_rate": 0.0},
            {"id": "c", "passed": True, "pass_rate": 0.66},
        ]
    }

    diff = compare_runs(previous, current)

    assert diff == {"corrected": ["a"], "regressed": ["b"], "noisy": ["c"]}


def test_reference_smoke_ejecuta_los_sql_esperados(semantic_database) -> None:
    from eph_agent.database.sqlite import SQLiteAdapter
    from eph_agent.evaluation import run_reference_smoke

    cases = load_cases(RAIZ / "eval" / "golden.yml")
    adapter = SQLiteAdapter(semantic_database)
    try:
        result = run_reference_smoke(cases, adapter, repetitions=1)
    finally:
        adapter.close()

    assert result["summary"] == {
        "total": 13,
        "passed": 13,
        "pass_rate": 1.0,
        "repetitions": 1,
        "skipped": 3,
    }
