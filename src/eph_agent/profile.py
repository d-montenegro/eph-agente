"""Profiling reproducible de las vistas semánticas."""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path
from typing import Any

_IDENTIFIER = re.compile(r"^[a-z_][a-z0-9_]*$")


def profile_view(
    connection: sqlite3.Connection,
    view_name: str,
    max_values: int = 30,
) -> dict[str, Any]:
    """Calcula filas, nulos, distintos, rangos y valores más frecuentes."""
    if not _IDENTIFIER.fullmatch(view_name):
        raise ValueError(f"Nombre de vista inválido: {view_name!r}")

    exists = connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type IN ('view', 'table') AND name = ?",
        (view_name,),
    ).fetchone()
    if not exists:
        raise ValueError(f"No existe la vista {view_name!r}")

    columns = [row[1] for row in connection.execute(f'PRAGMA table_info("{view_name}")')]
    total = connection.execute(f'SELECT COUNT(*) FROM "{view_name}"').fetchone()[0]
    result: dict[str, Any] = {"view": view_name, "rows": total, "columns": {}}

    for column in columns:
        quoted = f'"{column}"'
        nulls = connection.execute(
            f'SELECT COUNT(*) FROM "{view_name}" WHERE {quoted} IS NULL'
        ).fetchone()[0]
        distinct = connection.execute(
            f'SELECT COUNT(DISTINCT {quoted}) FROM "{view_name}"'
        ).fetchone()[0]
        types = {
            row[0]
            for row in connection.execute(f'SELECT DISTINCT typeof({quoted}) FROM "{view_name}"')
        } - {"null"}

        info: dict[str, Any] = {"nulls": nulls, "distinct": distinct}
        if types and types <= {"integer", "real"}:
            info["kind"] = "numeric"
            minimum, maximum, mean = connection.execute(
                f'SELECT MIN({quoted}), MAX({quoted}), AVG({quoted}) FROM "{view_name}"'
            ).fetchone()
            info.update(min=minimum, max=maximum, mean=mean)
        else:
            info["kind"] = "categorical"
            info["values"] = {
                str(value): count
                for value, count in connection.execute(
                    f"""
                    SELECT {quoted}, COUNT(*) FROM "{view_name}"
                    GROUP BY 1 ORDER BY 2 DESC, 1 LIMIT ?
                    """,
                    (max_values,),
                )
            }
        result["columns"][column] = info

    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Perfila una vista semántica de la EPH.")
    parser.add_argument("view", help="nombre de la vista (por ejemplo personas)")
    parser.add_argument("--db", type=Path, default=Path("eph.sqlite"))
    args = parser.parse_args(argv)

    connection = sqlite3.connect(args.db)
    try:
        print(json.dumps(profile_view(connection, args.view), ensure_ascii=False, indent=2))
    finally:
        connection.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
