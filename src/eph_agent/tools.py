"""Herramientas determinísticas del agente sobre la capa semántica."""

from __future__ import annotations

from typing import Any

from eph_agent.database.base import DatabaseAdapter, QueryResult


def describir_tabla(adapter: DatabaseAdapter, nombre: str) -> dict[str, Any]:
    """Devuelve la ficha completa de columnas de una vista semántica."""
    return {"view": nombre, "columns": adapter.describe_table(nombre)}


def ejecutar_sql(adapter: DatabaseAdapter, query: str) -> QueryResult:
    """Ejecuta una consulta de lectura acotada y devuelve el SQL realmente usado."""
    return adapter.execute(query)
