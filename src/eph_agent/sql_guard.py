"""Validación de consultas: una sola lectura, sobre vistas permitidas y acotada."""

from __future__ import annotations

import sqlglot
from sqlglot import exp
from sqlglot.errors import ParseError

ALLOWED_VIEWS = frozenset({"personas", "hogares"})
_READ_ROOTS = (exp.Select, exp.Union, exp.Intersect, exp.Except)


class SQLGuardError(ValueError):
    """La consulta no cumple el contrato de solo lectura."""


def validate_query(
    sql: str,
    *,
    allowed_views: frozenset[str] = ALLOWED_VIEWS,
    dialect: str = "sqlite",
    row_limit: int = 1_000,
) -> str:
    """Devuelve el SQL acotado o falla si no es una única lectura permitida.

    No se usa regex como defensa principal: la consulta se parsea y se valida
    sobre el árbol sintáctico. El resultado se envuelve en un ``SELECT`` externo
    con ``LIMIT`` para garantizar el techo de filas aunque el modelo no lo ponga.
    """
    if not sql or not sql.strip():
        raise SQLGuardError("La consulta está vacía")

    try:
        statements = [item for item in sqlglot.parse(sql, read=dialect) if item is not None]
    except ParseError as error:
        raise SQLGuardError(f"La consulta no se pudo interpretar: {error}") from error

    if len(statements) != 1:
        raise SQLGuardError("Solo se permite una única sentencia SQL")

    tree = statements[0]
    if not isinstance(tree, _READ_ROOTS):
        raise SQLGuardError("Solo se permiten consultas SELECT (incluidas CTE)")

    if tree.find(exp.Into):
        raise SQLGuardError("SELECT INTO no está permitido")
    if tree.find(exp.Placeholder):
        raise SQLGuardError("La consulta no admite parámetros; usá literales")

    tables = list(tree.find_all(exp.Table))
    cte_names = {cte.alias_or_name.lower() for cte in tree.find_all(exp.CTE)}
    names: set[str] = set()
    for table in tables:
        if table.db or table.catalog:
            raise SQLGuardError(
                f"No se permiten nombres calificados con esquema: {table.sql(dialect=dialect)}"
            )
        name = table.name
        if not name:
            raise SQLGuardError("La consulta referencia una tabla sin nombre")
        names.add(name.lower())

    names -= cte_names
    unknown = names - set(allowed_views)
    if unknown:
        raise SQLGuardError(
            "Solo se pueden consultar las vistas "
            f"{', '.join(sorted(allowed_views))}; se intentó: {', '.join(sorted(unknown))}"
        )

    if row_limit <= 0:
        raise ValueError("row_limit debe ser positivo")

    inner = sql.strip().rstrip(";").strip()
    return f"SELECT * FROM (\n{inner}\n) AS _guard LIMIT {int(row_limit)}"
