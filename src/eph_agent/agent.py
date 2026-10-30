"""Loop mínimo del agente: pregunta -> herramientas -> respuesta auditable."""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any

from eph_agent.answer import (
    AgentAnswer,
    ResultPayload,
    normalize_structured,
    parse_structured_answer,
    validate_agent_answer,
)
from eph_agent.database.base import DatabaseAdapter, DatabaseError, QueryResult
from eph_agent.prompts.schema_index import build_schema_index
from eph_agent.providers.base import LLMProvider, Message, ModelTurn, ToolCall, ToolDefinition
from eph_agent.sql_guard import SQLGuardError

SYSTEM_PROMPT_PATH = Path(__file__).resolve().parent / "prompts" / "system.md"

TOOL_DEFINITIONS = [
    ToolDefinition(
        name="describir_tabla",
        description=(
            "Devuelve la ficha completa de columnas de una vista semántica: "
            "descripción, valores, universo, NULL y ponderador."
        ),
        parameters={
            "type": "object",
            "properties": {
                "nombre": {"type": "string", "enum": ["personas", "hogares"]},
            },
            "required": ["nombre"],
        },
    ),
    ToolDefinition(
        name="ejecutar_sql",
        description=(
            "Ejecuta una única consulta SELECT de solo lectura sobre las vistas "
            "personas u hogares. Devuelve columnas, filas y el SQL ejecutado."
        ),
        parameters={
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    ),
]


class AgentError(RuntimeError):
    """El agente no pudo completar una respuesta auditable."""

    trace: list[dict[str, Any]] | None = None


def detect_period_conflict(question: str) -> str | None:
    """Detecta pedidos fuera del alcance 1T 2026."""
    years = {int(year) for year in re.findall(r"\b((?:19|20)\d{2})\b", question)}
    out_of_scope = sorted(year for year in years if year != 2026)
    if out_of_scope:
        return (
            "Los datos cargados cubren únicamente el 1T 2026; "
            f"no puedo responder sobre {out_of_scope[0]}."
        )

    quarters: set[int] = {int(value) for value in re.findall(r"\b([1-4])\s*[tT]\b", question)}
    quarters |= {
        int(value)
        for value in re.findall(r"\b([1-4])\s*(?:er|do|ro|to|°|º)?\s*trimestre\b", question)
    }
    words = {"primer": 1, "segundo": 2, "tercer": 3, "cuarto": 4}
    for word, number in words.items():
        if re.search(rf"\b{word}\s+trimestre\b", question, flags=re.IGNORECASE):
            quarters.add(number)

    if any(quarter != 1 for quarter in quarters):
        return "Los datos cargados cubren únicamente el 1T 2026, no otro trimestre."
    return None


def quality_warnings(result: ResultPayload, sample_size: int, truncated: bool) -> list[str]:
    warnings: list[str] = []
    if result.kind == "table" and not result.rows:
        warnings.append("La consulta no devolvió filas.")
    if result.kind == "scalar" and result.value is None:
        warnings.append("La consulta no devolvió un valor.")
    if truncated:
        warnings.append("El resultado se truncó al límite de filas configurado.")
    if result.kind == "table" and 0 < sample_size < 30:
        warnings.append(f"Pocas filas en el resultado (n={sample_size}); interpretar con cautela.")
    return warnings


class AgentService:
    """Orquesta como máximo ``max_turns`` llamadas al modelo."""

    def __init__(
        self,
        adapter: DatabaseAdapter,
        provider: LLMProvider,
        *,
        model: str | None = None,
        profile: str = "local",
        max_turns: int = 6,
        system_prompt: str | None = None,
        debug: bool = False,
    ) -> None:
        self.adapter = adapter
        self.provider = provider
        self.model = model or getattr(provider, "model", "")
        self.profile = profile
        self.max_turns = max(1, max_turns)
        self._system_prompt = system_prompt
        self.debug = debug

    async def ask(self, question: str) -> AgentAnswer:
        if not question.strip():
            raise AgentError("La pregunta está vacía")

        trace: list[dict[str, Any]] = []
        conflict = detect_period_conflict(question)
        if conflict:
            if self.debug:
                trace.append({"event": "period_conflict", "detail": conflict})
            return validate_agent_answer(
                {
                    "result": ResultPayload().model_dump(),
                    "sql": None,
                    "assumptions": [],
                    "warnings": [conflict],
                    "answer": conflict,
                    "profile": self.profile,
                    "model": self.model,
                    "sample_size": 0,
                    "trace": trace if self.debug else None,
                }
            )

        messages = [
            Message(role="system", content=self._render_system_prompt()),
            Message(role="user", content=question),
        ]
        last_result: QueryResult | None = None

        for turn_number in range(1, self.max_turns + 1):
            started = time.perf_counter()
            reply: ModelTurn = await self.provider.complete_with_tools(
                messages,
                TOOL_DEFINITIONS,
                model=self.model,
                temperature=0.0,
            )
            entry: dict[str, Any] = {
                "turn": turn_number,
                "elapsed_ms": round((time.perf_counter() - started) * 1_000, 2),
                "content": reply.content,
                "tool_calls": [
                    {"name": call.name, "arguments": call.arguments} for call in reply.tool_calls
                ],
                "tool_results": [],
            }

            if reply.tool_calls:
                messages.append(
                    Message(
                        role="assistant",
                        content=reply.content,
                        tool_calls=reply.tool_calls,
                    )
                )
                for call in reply.tool_calls:
                    payload, result = self._run_tool(call)
                    entry["tool_results"].append({"name": call.name, "result": payload})
                    messages.append(
                        Message(
                            role="tool",
                            tool_call_id=call.id,
                            content=json.dumps(payload, ensure_ascii=False, default=str),
                        )
                    )
                    if result is not None:
                        last_result = result
                trace.append(entry)
                continue

            trace.append(entry)
            return self._finalize(reply.content, last_result, trace)

        error = AgentError(
            f"No se pudo completar la consulta en {self.max_turns} turnos. "
            "No se devuelve una respuesta inventada."
        )
        if self.debug:
            error.trace = trace
        raise error

    def _render_system_prompt(self) -> str:
        template = self._system_prompt
        if template is None:
            template = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
        return template.replace("{{SCHEMA_INDEX}}", self._schema_index())

    def _schema_index(self) -> str:
        try:
            views = self.adapter.views()
            columns_by_view = {
                view["view"]: self.adapter.describe_table(view["view"]) for view in views
            }
        except (DatabaseError, ValueError) as error:
            raise AgentError(f"No se pudo leer la capa semántica: {error}") from error
        return build_schema_index(views, columns_by_view)

    def _run_tool(self, call: ToolCall) -> tuple[dict[str, Any], QueryResult | None]:
        if call.name == "describir_tabla":
            name = str(call.arguments.get("nombre") or "")
            try:
                columns = self.adapter.describe_table(name)
            except (DatabaseError, ValueError) as error:
                return {"error": str(error)}, None
            return {"view": name, "columns": columns}, None

        if call.name == "ejecutar_sql":
            query = call.arguments.get("query")
            if not isinstance(query, str) or not query.strip():
                return {"error": "Falta la consulta SQL"}, None
            try:
                result = self.adapter.execute(query)
            except (DatabaseError, SQLGuardError, ValueError) as error:
                return {"error": str(error)}, None
            return {
                "columns": result.columns,
                "rows": result.rows,
                "row_count": result.row_count,
                "truncated": result.truncated,
                "sql": result.sql,
            }, result

        return {"error": f"Herramienta desconocida: {call.name}"}, None

    def _finalize(
        self,
        content: str | None,
        last_result: QueryResult | None,
        trace: list[dict[str, Any]] | None = None,
    ) -> AgentAnswer:
        parsed = parse_structured_answer(content)
        structured = normalize_structured(parsed)
        warnings = list(structured["warnings"])
        answer_text = structured["answer"].strip()

        if parsed is None:
            answer_text = (content or "").strip()
            warnings.append("La respuesta del modelo no siguió el formato estructurado.")
        elif not answer_text:
            answer_text = "La consulta se ejecutó; revisá el resultado estructurado."

        if last_result is None:
            result_payload = ResultPayload()
            warnings.append(
                "No se ejecutó ninguna consulta SQL; la respuesta no está respaldada por datos."
            )
            sample_size = 0
        else:
            result_payload = _to_payload(last_result)
            warnings.extend(
                quality_warnings(result_payload, last_result.row_count, last_result.truncated)
            )
            sample_size = last_result.row_count

        return validate_agent_answer(
            {
                "result": result_payload.model_dump(),
                "sql": last_result.sql if last_result is not None else None,
                "assumptions": structured["assumptions"],
                "warnings": _dedupe(warnings),
                "answer": answer_text or "No se pudo generar una respuesta en texto.",
                "profile": self.profile,
                "model": self.model,
                "sample_size": sample_size,
                "trace": trace if self.debug else None,
            }
        )


def _to_payload(result: QueryResult) -> ResultPayload:
    is_scalar = len(result.columns) == 1 and len(result.rows) == 1
    return ResultPayload(
        kind="scalar" if is_scalar else "table",
        value=result.rows[0][0] if is_scalar else None,
        columns=result.columns,
        rows=result.rows,
    )


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered
