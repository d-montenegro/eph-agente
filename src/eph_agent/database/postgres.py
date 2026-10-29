"""Adaptador PostgreSQL de solo lectura."""

from __future__ import annotations

import time
from typing import Any

from eph_agent.database.base import (
    DatabaseError,
    QueryExecutionError,
    QueryResult,
    QueryTimeoutError,
)
from eph_agent.semantic import describe_table as read_column_metadata
from eph_agent.semantic import list_views
from eph_agent.sql_guard import validate_query


class PostgresAdapter:
    """Usa una transacción read-only y ``statement_timeout`` por consulta."""

    def __init__(
        self,
        dsn: str,
        *,
        row_limit: int = 1_000,
        timeout_ms: int = 5_000,
    ) -> None:
        self.dsn = dsn
        self.row_limit = row_limit
        self.timeout_ms = timeout_ms
        self._connection: Any | None = None

    def connect(self) -> Any:
        if self._connection is not None:
            return self._connection
        try:
            import psycopg
        except ImportError as error:
            raise DatabaseError(
                "Falta el driver de PostgreSQL; instalá el extra 'postgres'"
            ) from error
        connection = psycopg.connect(self.dsn)
        connection.execute("SET SESSION CHARACTERISTICS AS TRANSACTION READ ONLY")
        connection.execute(f"SET statement_timeout = {int(self.timeout_ms)}")
        self._connection = connection
        return connection

    def execute(self, sql: str) -> QueryResult:
        connection = self.connect()
        # Se pide una fila extra para detectar truncamiento sin confiar en el modelo.
        guarded = validate_query(sql, dialect="postgres", row_limit=self.row_limit + 1)
        started = time.monotonic()
        try:
            with connection.cursor() as cursor:
                cursor.execute(guarded)
                columns = [item.name for item in cursor.description or []]
                rows = cursor.fetchmany(self.row_limit + 1)
        except Exception as error:  # psycopg.QueryCanceled y errores de sintaxis
            if error.__class__.__name__ == "QueryCanceled":
                raise QueryTimeoutError(
                    f"La consulta superó el límite de {self.timeout_ms} ms"
                ) from error
            raise QueryExecutionError(f"Error al ejecutar la consulta: {error}") from error
        finally:
            connection.rollback()

        truncated = len(rows) > self.row_limit
        rows = rows[: self.row_limit]
        return QueryResult(
            columns=columns,
            rows=[list(row) for row in rows],
            sql=guarded,
            elapsed_ms=round((time.monotonic() - started) * 1_000, 2),
            truncated=truncated,
        )

    def describe_table(self, view_name: str) -> list[dict[str, Any]]:
        return read_column_metadata(self.connect(), view_name)

    def views(self) -> list[dict[str, Any]]:
        return list_views(self.connect())

    def close(self) -> None:
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def __enter__(self) -> PostgresAdapter:
        self.connect()
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()
