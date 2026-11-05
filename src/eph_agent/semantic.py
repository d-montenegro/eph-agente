"""Instalación y validación de la capa semántica de la EPH."""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any

import yaml

from eph_agent.paths import repo_root

PACKAGE_ROOT = repo_root()
SEMANTIC_DIR = PACKAGE_ROOT / "semantic"
VIEWS_SQL = SEMANTIC_DIR / "views.sql"
SCHEMA_SQL = SEMANTIC_DIR / "schema.sql"
COLUMNS_YML = SEMANTIC_DIR / "columns.yml"


class SemanticLayerError(ValueError):
    """La capa semántica no coincide con el diccionario o con los datos."""


def load_dictionary(path: Path | None = None) -> dict[str, Any]:
    """Carga el diccionario versionado de columnas."""
    source = Path(path) if path is not None else COLUMNS_YML
    with source.open(encoding="utf-8") as handle:
        dictionary = yaml.safe_load(handle)
    _check_dictionary_structure(dictionary, source)
    return dictionary


def _check_dictionary_structure(dictionary: Any, source: Path) -> None:
    if not isinstance(dictionary, dict) or "views" not in dictionary or "period" not in dictionary:
        raise SemanticLayerError(f"{source} debe declarar 'period' y 'views'")
    for view_name, spec in dictionary["views"].items():
        if not spec.get("source_table"):
            raise SemanticLayerError(f"La vista {view_name} no declara source_table")
        columns = spec.get("columns") or {}
        if not columns:
            raise SemanticLayerError(f"La vista {view_name} no declara columnas")
        for column_name, column in columns.items():
            for required in ("description", "type", "null_meaning", "universe"):
                if not column.get(required):
                    raise SemanticLayerError(f"{view_name}.{column_name} no declara '{required}'")


def _statements(sql: str) -> list[str]:
    """Separa un script SQL en sentencias, ignorando líneas de comentario."""
    lines = [line for line in sql.splitlines() if not line.strip().startswith("--")]
    return [statement.strip() for statement in "\n".join(lines).split(";") if statement.strip()]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def view_definition(view_name: str, path: Path | None = None) -> str:
    """Devuelve el SELECT versionado que define una vista semántica."""
    if view_name not in load_dictionary()["views"]:
        raise SemanticLayerError(f"No existe la vista semántica {view_name!r}")
    sql = _read(Path(path) if path is not None else VIEWS_SQL)
    marker = f"CREATE VIEW {view_name} AS"
    try:
        definition = sql.split(marker, 1)[1].split(";", 1)[0].strip()
    except IndexError as error:
        raise SemanticLayerError(f"No se encontró la definición SQL de {view_name!r}") from error
    return definition


def install_semantic_layer(
    connection: sqlite3.Connection,
    dictionary: dict[str, Any] | None = None,
    semantic_dir: Path | None = None,
) -> dict[str, Any]:
    """Crea las vistas y reemplaza los metadatos en una única transacción."""
    directory = Path(semantic_dir) if semantic_dir is not None else SEMANTIC_DIR
    dictionary = dictionary or load_dictionary(directory / "columns.yml")
    period = dictionary["period"]

    with connection:
        for statement in _statements(_read(directory / "schema.sql")):
            connection.execute(statement)
        for statement in _statements(_read(directory / "views.sql")):
            connection.execute(statement)

        connection.execute("DELETE FROM semantic_columns")
        connection.execute("DELETE FROM semantic_views")

        total_columns = 0
        for view_name, spec in dictionary["views"].items():
            connection.execute(
                """
                INSERT INTO semantic_views
                    (view_name, source_table, description, period_anio, period_trimestre)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    view_name,
                    spec["source_table"],
                    spec["description"].strip(),
                    period["anio"],
                    period["trimestre"],
                ),
            )
            for column_name, column in spec["columns"].items():
                connection.execute(
                    """
                    INSERT INTO semantic_columns (
                        view_name, column_name, source_column, description, data_type,
                        possible_values, null_meaning, universe, weight, synonyms, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        view_name,
                        column_name,
                        column.get("source"),
                        column["description"],
                        column["type"],
                        _to_json(column.get("possible_values")),
                        column.get("null_meaning"),
                        column.get("universe"),
                        column.get("weight"),
                        _to_json(column.get("synonyms", [])),
                        column.get("notes"),
                    ),
                )
                total_columns += 1

    return {
        "views": sorted(dictionary["views"]),
        "columns": total_columns,
        "period": period,
    }


def _to_json(value: Any) -> str | None:
    if value is None:
        return None
    return json.dumps(value, ensure_ascii=False)


def _table_columns(connection: sqlite3.Connection, name: str, kind: str) -> set[str] | None:
    exists = connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type = ? AND name = ?", (kind, name)
    ).fetchone()
    if not exists:
        return None
    return {row[1] for row in connection.execute(f'PRAGMA table_info("{name}")')}


def validate_dictionary(
    connection: sqlite3.Connection,
    dictionary: dict[str, Any] | None = None,
    semantic_dir: Path | None = None,
) -> None:
    """Falla si las vistas, los datos o los tipos no coinciden con el diccionario."""
    directory = Path(semantic_dir) if semantic_dir is not None else SEMANTIC_DIR
    dictionary = dictionary or load_dictionary(directory / "columns.yml")
    period = dictionary["period"]
    problems: list[str] = []

    for view_name, spec in dictionary["views"].items():
        source_table = spec["source_table"]
        source_columns = _table_columns(connection, source_table, "table")
        if source_columns is None:
            problems.append(f"falta la tabla cruda {source_table} (vista {view_name})")
            continue

        view_columns = _table_columns(connection, view_name, "view")
        if view_columns is None:
            problems.append(f"falta la vista {view_name}")
            continue

        declared = set(spec["columns"])
        missing = declared - view_columns
        extra = view_columns - declared
        if missing:
            problems.append(
                f"{view_name}: columnas declaradas ausentes en la vista: {sorted(missing)}"
            )
        if extra:
            problems.append(f"{view_name}: columnas de la vista sin metadatos: {sorted(extra)}")

        source_rows = connection.execute(f'SELECT COUNT(*) FROM "{source_table}"').fetchone()[0]
        view_rows = connection.execute(f'SELECT COUNT(*) FROM "{view_name}"').fetchone()[0]
        if source_rows != view_rows:
            problems.append(f"{view_name}: filas {view_rows} != filas crudas {source_rows}")

        periods = {
            tuple(row)
            for row in connection.execute(f'SELECT DISTINCT ANO4, TRIMESTRE FROM "{source_table}"')
        }
        expected = {(period["anio"], period["trimestre"])}
        if periods != expected:
            problems.append(f"{view_name}: períodos {sorted(periods)} != {sorted(expected)}")

        for column_name, column in spec["columns"].items():
            if column_name not in view_columns:
                continue
            source_column = column.get("source")
            if source_column and source_column not in source_columns:
                problems.append(
                    f"{view_name}.{column_name}: falta la columna cruda {source_column}"
                )
            weight = column.get("weight")
            if weight and weight not in declared:
                problems.append(
                    f"{view_name}.{column_name}: el ponderador {weight} "
                    "no es una columna de la vista"
                )
            problems.extend(_check_column_values(connection, view_name, column_name, column))

    for check in dictionary.get("validation", []):
        name = check.get("name")
        sql = check.get("sql")
        expected_value = check.get("expected")
        if not name or not sql or expected_value is None:
            problems.append(f"check de validación inválido: {check!r}")
            continue
        try:
            actual = connection.execute(sql).fetchone()[0]
        except sqlite3.Error as error:
            problems.append(f"check {name}: error al ejecutar ({error})")
            continue
        if actual != expected_value:
            description = check.get("description", "")
            problems.append(f"check {name}: {actual} != {expected_value} ({description})")

    if problems:
        raise SemanticLayerError(
            "La capa semántica no coincide con el diccionario:\n- " + "\n- ".join(problems)
        )


def _check_column_values(
    connection: sqlite3.Connection,
    view_name: str,
    column_name: str,
    column: dict[str, Any],
) -> list[str]:
    problems: list[str] = []
    quoted = f'"{column_name}"'

    types = {
        row[0] for row in connection.execute(f'SELECT DISTINCT typeof({quoted}) FROM "{view_name}"')
    } - {"null"}

    data_type = column["type"]
    if data_type == "numerica" and types - {"integer", "real"}:
        problems.append(
            f"{view_name}.{column_name}: se esperaba numérica y hay tipos {sorted(types)}"
        )
    if data_type == "booleana" and types - {"integer"}:
        problems.append(
            f"{view_name}.{column_name}: se esperaba booleana 0/1 y hay tipos {sorted(types)}"
        )
    if data_type == "categorica" and types - {"text"}:
        problems.append(
            f"{view_name}.{column_name}: se esperaba categórica de texto "
            f"y hay tipos {sorted(types)}"
        )

    values = column.get("possible_values")
    if values is not None:
        documented = {str(value) for value in values}
        actual = {
            str(row[0])
            for row in connection.execute(
                f'SELECT DISTINCT {quoted} FROM "{view_name}" WHERE {quoted} IS NOT NULL'
            )
        }
        undocumented = actual - documented
        if undocumented:
            problems.append(
                f"{view_name}.{column_name}: valores no documentados {sorted(undocumented)}"
            )
    return problems


def list_views(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    """Devuelve las vistas semánticas con su descripción y período."""
    rows = connection.execute(
        """
        SELECT view_name, source_table, description, period_anio, period_trimestre
        FROM semantic_views
        ORDER BY view_name
        """
    ).fetchall()
    return [
        {
            "view": row[0],
            "source_table": row[1],
            "description": row[2],
            "period": {"anio": row[3], "trimestre": row[4]},
        }
        for row in rows
    ]


def describe_table(connection: sqlite3.Connection, view_name: str) -> list[dict[str, Any]]:
    """Devuelve la ficha completa de columnas de una vista semántica."""
    dictionary_columns = load_dictionary()["views"].get(view_name, {}).get("columns", {})
    rows = connection.execute(
        """
        SELECT column_name, source_column, description, data_type, possible_values,
               null_meaning, universe, weight, synonyms, notes
        FROM semantic_columns
        WHERE view_name = ?
        ORDER BY rowid
        """,
        (view_name,),
    ).fetchall()
    if not rows:
        raise SemanticLayerError(
            f"No existe la vista semántica {view_name!r}. Disponibles: "
            + ", ".join(item["view"] for item in list_views(connection))
        )
    return [
        {
            "column": row[0],
            "source_column": row[1],
            "description": row[2],
            "type": row[3],
            "possible_values": _from_json(row[4]),
            "null_meaning": row[5],
            "universe": row[6],
            "weight": row[7],
            "synonyms": _from_json(row[8]) or [],
            "notes": row[9],
            "sql_expression": dictionary_columns.get(row[0], {}).get("sql_expression"),
            "raw_values": dictionary_columns.get(row[0], {}).get("raw_values"),
        }
        for row in rows
    ]


def _from_json(value: str | None) -> Any:
    if value is None:
        return None
    return json.loads(value)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Instala y valida la capa semántica de la EPH.")
    parser.add_argument("--db", type=Path, default=PACKAGE_ROOT / "eph.sqlite")
    parser.add_argument(
        "--validate",
        action="store_true",
        help="valida el diccionario contra los datos después de instalar",
    )
    args = parser.parse_args(argv)

    connection = sqlite3.connect(args.db)
    try:
        summary = install_semantic_layer(connection)
        print(f"Vistas instaladas: {', '.join(summary['views'])}")
        print(f"Columnas documentadas: {summary['columns']}")
        if args.validate:
            validate_dictionary(connection)
            print("Diccionario validado contra los datos.")
    except SemanticLayerError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    finally:
        connection.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
