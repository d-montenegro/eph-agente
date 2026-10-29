"""Contrato común de los backends de datos."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


class DatabaseError(RuntimeError):
    """Error de acceso a datos seguro para devolver al cliente."""


class QueryExecutionError(DatabaseError):
    """La consulta falló al ejecutarse en el motor."""


class QueryTimeoutError(DatabaseError):
    """La consulta superó el tiempo máximo permitido."""


@dataclass(frozen=True, slots=True)
class QueryResult:
    """Resultado acotado de una consulta de lectura."""

    columns: list[str]
    rows: list[list[Any]] = field(default_factory=list)
    sql: str = ""
    elapsed_ms: float = 0.0
    truncated: bool = False

    @property
    def row_count(self) -> int:
        return len(self.rows)


class DatabaseAdapter(Protocol):
    """Superficie mínima que consume el agente, sin depender del motor."""

    def execute(self, sql: str) -> QueryResult: ...

    def describe_table(self, view_name: str) -> list[dict[str, Any]]: ...

    def views(self) -> list[dict[str, Any]]: ...

    def close(self) -> None: ...
