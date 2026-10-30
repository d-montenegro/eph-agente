"""Contrato de salida del agente y validación."""

from __future__ import annotations

import json
import re
from typing import Any, Literal

from pydantic import BaseModel, Field


class AnswerValidationError(ValueError):
    """La respuesta del agente no cumple el contrato auditable."""


class ResultPayload(BaseModel):
    kind: Literal["scalar", "table"] = "scalar"
    value: Any = None
    columns: list[str] = Field(default_factory=list)
    rows: list[list[Any]] = Field(default_factory=list)


class AgentAnswer(BaseModel):
    result: ResultPayload = Field(default_factory=ResultPayload)
    sql: str | None = None
    assumptions: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    answer: str
    profile: str
    model: str
    sample_size: int = 0
    trace: list[dict[str, Any]] | None = None


def parse_structured_answer(content: str | None) -> dict[str, Any] | None:
    """Extrae el JSON final aunque venga dentro de un bloque de código."""
    if not content:
        return None
    text = content.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z0-9_-]*\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end <= start:
        return None
    try:
        payload = json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def normalize_structured(payload: dict[str, Any] | None) -> dict[str, Any]:
    """Acepta las claves del contrato y sus equivalentes en español."""
    if not payload:
        return {"answer": "", "assumptions": [], "warnings": [], "result": None}
    result = (
        payload.get("result") if payload.get("result") is not None else payload.get("resultado")
    )
    return {
        "answer": payload.get("answer") or payload.get("respuesta") or "",
        "assumptions": _as_list(payload.get("assumptions") or payload.get("supuestos")),
        "warnings": _as_list(payload.get("warnings") or payload.get("advertencias")),
        "result": result,
    }


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return [str(item) for item in value]


def validate_agent_answer(payload: dict[str, Any] | AgentAnswer) -> AgentAnswer:
    """Valida el contrato mínimo de una respuesta auditable."""
    answer = payload if isinstance(payload, AgentAnswer) else AgentAnswer.model_validate(payload)
    if not answer.answer.strip():
        raise AnswerValidationError("La respuesta en texto no puede estar vacía")
    has_data = answer.result.value is not None or bool(answer.result.rows)
    if has_data and not answer.sql:
        raise AnswerValidationError("Una respuesta con datos debe incluir el SQL ejecutado")
    return answer
