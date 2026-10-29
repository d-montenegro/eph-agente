"""Evaluación reproducible del agente contra un golden set."""

from __future__ import annotations

import argparse
import asyncio
import json
import subprocess
import sys
import time
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import sqlglot
import yaml
from sqlglot import exp
from sqlglot.errors import ParseError

ASK = Callable[[str], Awaitable[Any]]
DEFAULT_REPETITIONS = 3
VALID_TYPES = {"numero", "tabla", "rechazo", "sin_datos"}


class EvaluationError(ValueError):
    """El caso o la corrida no tienen el formato esperado."""


def load_cases(path: Path | str) -> list[dict[str, Any]]:
    source = Path(path)
    data = yaml.safe_load(source.read_text(encoding="utf-8"))
    cases = data.get("casos") if isinstance(data, dict) else data
    if not isinstance(cases, list) or not cases:
        raise EvaluationError(f"{source} no contiene una lista de casos")
    for case in cases:
        for key in ("id", "pregunta", "tipo", "categoria", "dificultad", "fuente"):
            if not case.get(key):
                raise EvaluationError(f"El caso {case.get('id', '?')} no declara {key!r}")
        if case["tipo"] not in VALID_TYPES:
            raise EvaluationError(
                f"El caso {case['id']} usa tipo {case['tipo']!r}; válidos: {sorted(VALID_TYPES)}"
            )
        if case["tipo"] == "numero" and "valor_esperado" not in case:
            raise EvaluationError(f"El caso {case['id']} necesita valor_esperado")
    return cases


def normalize_number(value: float, unidad: str) -> float:
    if unidad == "fraccion" and abs(value) > 1.5:
        return value / 100
    if unidad == "porcentaje" and abs(value) <= 1.5:
        return value * 100
    return value


def extract_scalar(answer: dict[str, Any]) -> Any:
    result = answer.get("result") or {}
    if result.get("kind") == "scalar":
        return result.get("value")
    rows = result.get("rows") or []
    if len(rows) == 1 and len(rows[0]) == 1:
        return rows[0][0]
    return None


def compare_result(
    actual: dict[str, Any],
    expected: dict[str, Any],
) -> dict[str, Any]:
    tipo = expected["tipo"]
    if tipo == "numero":
        value = extract_scalar(actual)
        target = expected["valor_esperado"]
        if value is None:
            return {"ok": False, "detail": "La respuesta no trae un valor escalar", "actual": None}
        unidad = expected.get("unidad", "absoluta")
        tolerance = float(expected.get("tolerancia", 0))
        value = normalize_number(float(value), unidad)
        target = normalize_number(float(target), unidad)
        ok = abs(value - target) <= tolerance
        return {
            "ok": ok,
            "actual": value,
            "expected": target,
            "tolerance": tolerance,
            "detail": None if ok else f"{value} != {target} (tol {tolerance})",
        }

    if tipo == "tabla":
        result = actual.get("result") or {}
        if result.get("kind") != "table":
            return {"ok": False, "detail": "La respuesta no es una tabla"}
        columns = result.get("columns") or []
        rows = result.get("rows") or []
        expected_columns = expected.get("columns") or []
        expected_rows = expected.get("rows") or []
        if set(columns) != set(expected_columns):
            return {
                "ok": False,
                "detail": f"columnas {columns} != {expected_columns}",
            }
        tolerance = float(expected.get("tolerancia", 0))
        orden = bool(expected.get("orden", False))
        actual_normalized = _row_maps(columns, rows)
        expected_normalized = _row_maps(expected_columns, expected_rows)
        if not orden:
            actual_normalized.sort(key=lambda row: json.dumps(row, sort_keys=True))
            expected_normalized.sort(key=lambda row: json.dumps(row, sort_keys=True))
        ok = len(actual_normalized) == len(expected_normalized) and all(
            _row_equal(left, right, tolerance)
            for left, right in zip(actual_normalized, expected_normalized, strict=False)
        )
        return {"ok": ok, "detail": None if ok else "las filas no coinciden"}

    if tipo == "rechazo":
        text = f"{actual.get('answer', '')} {' '.join(actual.get('warnings') or [])}"
        ok = actual.get("sql") is None and "1T 2026" in text
        return {"ok": ok, "detail": None if ok else "no se aclaró el período 1T 2026"}

    if tipo == "sin_datos":
        value = extract_scalar(actual)
        result = actual.get("result") or {}
        rows = result.get("rows") or []
        ok = value is None and not rows
        return {"ok": ok, "detail": None if ok else "la respuesta inventó datos"}

    raise EvaluationError(f"Tipo de caso desconocido: {tipo}")


def _row_maps(columns: list[str], rows: list[list[Any]]) -> list[dict[str, Any]]:
    return [dict(zip(columns, row, strict=False)) for row in rows]


def _row_equal(left: dict[str, Any], right: dict[str, Any], tolerance: float) -> bool:
    if set(left) != set(right):
        return False
    for key in left:
        a, b = left[key], right[key]
        if isinstance(a, int | float) and isinstance(b, int | float):
            if abs(float(a) - float(b)) > tolerance:
                return False
        elif str(a).strip() != str(b).strip():
            return False
    return True


def inspect_sql(sql: str | None, rules: dict[str, Any] | None) -> list[str]:
    """Verifica vistas, ponderadores y textos exigidos por el caso."""
    rules = rules or {}
    violations: list[str] = []
    if not sql:
        if rules:
            return ["No se ejecutó SQL"]
        return violations

    try:
        tree = sqlglot.parse_one(sql, read="sqlite")
    except ParseError as error:
        return [f"SQL inválido: {error}"]

    cte_names = {cte.alias_or_name.lower() for cte in tree.find_all(exp.CTE)}
    tables = {
        table.name.lower()
        for table in tree.find_all(exp.Table)
        if table.name.lower() not in cte_names
    }
    required_views = {view.lower() for view in rules.get("vistas") or []}
    forbidden = tables - required_views if required_views else set()
    if forbidden:
        violations.append(f"usa vistas no esperadas: {sorted(forbidden)}")

    columns = {column.name.lower() for column in tree.find_all(exp.Column)}
    for required in rules.get("columnas") or []:
        if required.lower() not in columns:
            violations.append(f"falta la columna {required}")

    text = sql.lower()
    for fragment in rules.get("texto") or []:
        if str(fragment).lower() not in text:
            violations.append(f"falta el filtro {fragment!r}")
    return violations


async def run_case(
    case: dict[str, Any],
    ask: ASK,
    repetitions: int = 1,
) -> dict[str, Any]:
    if repetitions < 1:
        raise EvaluationError("repetitions debe ser al menos 1")
    attempts: list[dict[str, Any]] = []

    for repetition in range(1, repetitions + 1):
        started = time.perf_counter()
        try:
            response = await ask(case["pregunta"])
            answer = _as_dict(response)
            comparison = compare_result(answer, case)
            sql_violations = inspect_sql(answer.get("sql"), case.get("reglas_sql"))
            ok = bool(comparison["ok"]) and not sql_violations
            error = None
        except Exception as exc:  # el fallo se registra, no corta la suite
            answer = {}
            comparison = {"ok": False, "detail": str(exc)}
            sql_violations = []
            ok = False
            error = f"{exc.__class__.__name__}: {exc}"

        attempts.append(
            {
                "repetition": repetition,
                "ok": ok,
                "latency_ms": round((time.perf_counter() - started) * 1_000, 2),
                "sql": answer.get("sql"),
                "result": answer.get("result"),
                "answer": answer.get("answer"),
                "warnings": answer.get("warnings") or [],
                "comparison": comparison,
                "sql_violations": sql_violations,
                "error": error,
            }
        )

    passed = sum(1 for attempt in attempts if attempt["ok"])
    return {
        "id": case["id"],
        "categoria": case["categoria"],
        "dificultad": case["dificultad"],
        "tipo": case["tipo"],
        "attempts": attempts,
        "passed": passed == repetitions,
        "pass_rate": passed / repetitions,
    }


async def run_suite(
    cases: list[dict[str, Any]],
    ask: ASK,
    repetitions: int = DEFAULT_REPETITIONS,
) -> dict[str, Any]:
    results = [await run_case(case, ask, repetitions) for case in cases]
    total = len(results)
    passed = sum(1 for result in results if result["passed"])
    return {
        "cases": results,
        "summary": {
            "total": total,
            "passed": passed,
            "pass_rate": passed / total if total else 0.0,
            "repetitions": repetitions,
        },
    }


def run_reference_smoke(
    cases: list[dict[str, Any]],
    adapter: Any,
    repetitions: int = 1,
) -> dict[str, Any]:
    """Ejecuta el ``sql_esperado`` como referencia determinística para CI.

    No usa un modelo: valida que los datos y la capa semántica sigan produciendo
    los valores del golden set. Sirve como smoke test de regresión en CI.
    """
    results: list[dict[str, Any]] = []
    for case in cases:
        sql = case.get("sql_esperado")
        if not sql or case["tipo"] in {"rechazo", "sin_datos"}:
            results.append({"id": case["id"], "skipped": True, "passed": True, "pass_rate": 1.0})
            continue
        attempts: list[dict[str, Any]] = []
        for _ in range(max(1, repetitions)):
            try:
                result = adapter.execute(sql)
                payload = {
                    "result": _result_dict(result),
                    "sql": result.sql,
                    "answer": "referencia",
                    "warnings": [],
                }
                comparison = compare_result(payload, case)
                violations = inspect_sql(result.sql, case.get("reglas_sql"))
                attempts.append(
                    {
                        "ok": bool(comparison["ok"]) and not violations,
                        "comparison": comparison,
                        "sql_violations": violations,
                    }
                )
            except Exception as exc:  # noqa: BLE001 - se registra el fallo
                attempts.append({"ok": False, "error": f"{exc.__class__.__name__}: {exc}"})
        passed = sum(1 for attempt in attempts if attempt["ok"])
        results.append(
            {
                "id": case["id"],
                "skipped": False,
                "attempts": attempts,
                "passed": passed == len(attempts),
                "pass_rate": passed / len(attempts),
            }
        )

    scored = [item for item in results if not item["skipped"]]
    total = len(scored)
    passed_cases = sum(1 for item in scored if item["passed"])
    return {
        "cases": results,
        "summary": {
            "total": total,
            "passed": passed_cases,
            "pass_rate": passed_cases / total if total else 0.0,
            "repetitions": repetitions,
            "skipped": len(results) - total,
        },
    }


def _result_dict(result: Any) -> dict[str, Any]:
    is_scalar = len(result.columns) == 1 and len(result.rows) == 1
    return {
        "kind": "scalar" if is_scalar else "table",
        "value": result.rows[0][0] if is_scalar else None,
        "columns": result.columns,
        "rows": result.rows,
    }


def compare_runs(previous: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    before = {case["id"]: case for case in previous.get("cases", [])}
    after = {case["id"]: case for case in current.get("cases", [])}
    corrected = sorted(
        cid for cid in after if cid in before and not before[cid]["passed"] and after[cid]["passed"]
    )
    regressed = sorted(
        cid for cid in after if cid in before and before[cid]["passed"] and not after[cid]["passed"]
    )
    noisy = sorted(
        cid
        for cid in after
        if cid in before
        and before[cid]["passed"] == after[cid]["passed"]
        and before[cid]["pass_rate"] != after[cid]["pass_rate"]
    )
    return {"corrected": corrected, "regressed": regressed, "noisy": noisy}


def save_run(
    result: dict[str, Any],
    directory: Path | str,
    *,
    profile: str,
    model: str,
    commit: str | None = None,
) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    path = target / f"{timestamp}-{profile}.json"
    payload = {
        "commit": commit or _current_commit(),
        "fecha": datetime.now(UTC).isoformat(),
        "profile": profile,
        "model": model,
        "summary": result.get("summary"),
        "cases": result.get("cases"),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def load_run(path: Path | str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _as_dict(answer: Any) -> dict[str, Any]:
    if isinstance(answer, dict):
        return answer
    if hasattr(answer, "model_dump"):
        return answer.model_dump()
    raise EvaluationError(f"Respuesta no convertible: {type(answer)!r}")


def _current_commit() -> str | None:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ejecuta el golden set sobre el agente.")
    parser.add_argument("--golden", type=Path, default=Path("eval/golden.yml"))
    parser.add_argument("--repetitions", type=int, default=DEFAULT_REPETITIONS)
    parser.add_argument("--profile", default="local")
    parser.add_argument("--out", type=Path, default=Path("eval/runs"))
    parser.add_argument(
        "--reference",
        action="store_true",
        help="ejecuta el sql_esperado sin modelo (smoke determinístico para CI)",
    )
    args = parser.parse_args(argv)

    from eph_agent.config import DatabaseSettings
    from eph_agent.database import create_database_adapter

    adapter = create_database_adapter(DatabaseSettings.from_env())
    try:
        if args.reference:
            result = run_reference_smoke(load_cases(args.golden), adapter, args.repetitions)
            profile_name, model_name = "reference", "sql_esperado"
        else:
            from eph_agent.agent import AgentService
            from eph_agent.providers import ProviderRegistry

            registry = ProviderRegistry.from_env()
            profile = registry.get(args.profile)
            provider = registry.create(profile.name)
            service = AgentService(adapter, provider, model=provider.model, profile=profile.name)
            result = asyncio.run(run_suite(load_cases(args.golden), service.ask, args.repetitions))
            profile_name, model_name = profile.name, provider.model
    finally:
        adapter.close()

    path = save_run(result, args.out, profile=profile_name, model=model_name)
    summary = result["summary"]
    skipped = summary.get("skipped", 0)
    print(
        f"Aprobados {summary['passed']}/{summary['total']} "
        f"({summary['pass_rate']:.0%}) · {skipped} sin SQL de referencia · "
        f"corrida guardada en {path}"
    )
    return 0 if summary["pass_rate"] >= 0.9 else 1


if __name__ == "__main__":
    sys.exit(main())
