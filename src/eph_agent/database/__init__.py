"""Selección del backend de datos sin acoplar el agente a un driver."""

from __future__ import annotations

from typing import Any

from eph_agent.config import DatabaseBackend, DatabaseSettings
from eph_agent.database.base import (
    DatabaseAdapter,
    DatabaseError,
    QueryExecutionError,
    QueryResult,
    QueryTimeoutError,
)
from eph_agent.database.d1 import D1Adapter
from eph_agent.database.postgres import PostgresAdapter
from eph_agent.database.sqlite import SQLiteAdapter


def create_database_adapter(settings: DatabaseSettings, **kwargs: Any) -> DatabaseAdapter:
    """Devuelve el adaptador correspondiente a la configuración validada."""
    if settings.backend is DatabaseBackend.SQLITE:
        return SQLiteAdapter(settings.sqlite_path(), **kwargs)
    if settings.backend is DatabaseBackend.POSTGRESQL:
        return PostgresAdapter(settings.url, **kwargs)
    return D1Adapter(settings, **kwargs)


__all__ = [
    "D1Adapter",
    "DatabaseAdapter",
    "DatabaseError",
    "PostgresAdapter",
    "QueryExecutionError",
    "QueryResult",
    "QueryTimeoutError",
    "SQLiteAdapter",
    "create_database_adapter",
]
