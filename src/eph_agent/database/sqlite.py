"""Adaptador SQLite de solo lectura con defensas en profundidad."""

from __future__ import annotations

import sqlite3
import time
from pathlib import Path
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

_ALLOWED_ACTIONS = {
    sqlite3.SQLITE_SELECT,
    sqlite3.SQLITE_READ,
    sqlite3.SQLITE_FUNCTION,
    sqlite3.SQLITE_RECURSIVE,
}


def _authorizer(
    action: int, arg1: str | None, arg2: str | None, dbname: str | None, trigger: str | None
) -> int:
    """Permite solo lectura; el parser ya limita las tablas a las vistas."""
    if action in _ALLOWED_ACTIONS:
        return sqlite3.SQLITE_OK
    return sqlite3.SQLITE_DENY


class SQLiteAdapter:
    """Abre la base con ``mode=ro``, ``query_only``, authorizer y timeout."""

    def __init__(
        self,
        database_path: Path | str,
        *,
        row_limit: int = 1_000,
        timeout_ms: int = 5_000,
    ) -> None:
        self.database_path = Path(database_path)
        self.row_limit = row_limit
        self.timeout_ms = timeout_ms
        self._connection: sqlite3.Connection | None = None

    def connect(self) -> sqlite3.Connection:
        if self._connection is not None:
            return self._connection
        if not self.database_path.exists():
            raise DatabaseError(f"No existe la base {self.database_path.name}")
        uri = f"file:{self.database_path}?mode=ro"
        # La conexión es por request y se usa en un solo hilo a la vez; FastAPI
        # crea la dependencia en un threadpool y la consume en el event loop.
        connection = sqlite3.connect(
            uri,
            uri=True,
            timeout=self.timeout_ms / 1_000,
            check_same_thread=False,
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA query_only = ON")
        connection.set_authorizer(_authorizer)
        self._connection = connection
        return connection

    def execute(self, sql: str) -> QueryResult:
        connection = self.connect()
        # Se pide una fila extra para detectar truncamiento sin confiar en el modelo.
        guarded = validate_query(sql, row_limit=self.row_limit + 1)
        deadline = time.monotonic() + self.timeout_ms / 1_000

        def _interrupt() -> int:
            return 1 if time.monotonic() > deadline else 0

        connection.set_progress_handler(_interrupt, 10_000)
        started = time.monotonic()
        try:
            cursor = connection.execute(guarded)
            rows = cursor.fetchmany(self.row_limit + 1)
            columns = [item[0] for item in cursor.description or []]
        except sqlite3.OperationalError as error:
            if "interrupted" in str(error):
                raise QueryTimeoutError(
                    f"La consulta superó el límite de {self.timeout_ms} ms"
                ) from error
            raise QueryExecutionError(f"Error al ejecutar la consulta: {error}") from error
        except sqlite3.Error as error:
            raise QueryExecutionError(f"Error al ejecutar la consulta: {error}") from error
        finally:
            connection.set_progress_handler(None, 0)

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

    def __enter__(self) -> SQLiteAdapter:
        self.connect()
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()
