"""Índice compacto de la capa semántica para el prompt del agente."""

from __future__ import annotations

from typing import Any


def build_schema_index(
    views: list[dict[str, Any]],
    columns_by_view: dict[str, list[dict[str, Any]]],
) -> str:
    """Genera un índice determinístico con vistas, columnas, valores y pesos."""
    lines: list[str] = ["Vistas semánticas disponibles (solo lectura, 1T 2026):"]
    for view in views:
        name = view["view"]
        lines.append(f"- {name} (desde {view['source_table']}): {view['description'].strip()}")
        for column in columns_by_view.get(name, []):
            lines.append("  - " + _describe_column(column))
    return "\n".join(lines)


def _describe_column(column: dict[str, Any]) -> str:
    parts = [f"{column['column']} [{column['type']}]: {column['description'].strip()}"]
    values = column.get("possible_values")
    if values:
        rendered = ", ".join(_render_value(value) for value in values)
        if len(values) > 12:
            rendered = ", ".join(_render_value(value) for value in values[:12]) + ", ..."
        parts.append(f"valores: {rendered}")
    if column.get("universe"):
        parts.append(f"universo: {column['universe'].strip()}")
    if column.get("weight"):
        parts.append(f"ponderador: {column['weight']}")
    if column.get("null_meaning"):
        parts.append(f"NULL: {column['null_meaning'].strip()}")
    return " | ".join(parts)


def _render_value(value: Any) -> str:
    return str(value)
