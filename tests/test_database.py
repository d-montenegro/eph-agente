import sqlite3

import pytest

from eph_agent.database.base import DatabaseError, QueryTimeoutError
from eph_agent.database.sqlite import SQLiteAdapter
from eph_agent.sql_guard import SQLGuardError


@pytest.fixture()
def adapter(semantic_database):
    instance = SQLiteAdapter(semantic_database, row_limit=1_000, timeout_ms=1_000)
    try:
        yield instance
    finally:
        instance.close()


def test_ejecuta_una_consulta_de_lectura(adapter) -> None:
    result = adapter.execute("SELECT COUNT(*) AS total FROM personas")

    assert result.columns == ["total"]
    assert result.rows == [[43_739]]
    assert "LIMIT 1001" in result.sql
    assert result.truncated is False


def test_rechaza_tablas_crudas(adapter) -> None:
    with pytest.raises(SQLGuardError, match="Solo se pueden consultar las vistas"):
        adapter.execute("SELECT * FROM individual")


def test_rechaza_escrituras_por_el_guard(adapter) -> None:
    with pytest.raises(SQLGuardError):
        adapter.execute("DELETE FROM personas")


def test_la_conexion_tambien_rechaza_escrituras(adapter) -> None:
    connection = adapter.connect()

    with pytest.raises(sqlite3.DatabaseError):
        connection.execute("CREATE TABLE intruso (valor INTEGER)")


def test_acota_las_filas_devueltas(semantic_database) -> None:
    instance = SQLiteAdapter(semantic_database, row_limit=5)
    try:
        result = instance.execute("SELECT codusu FROM personas")
    finally:
        instance.close()

    assert result.row_count == 5
    assert result.truncated is True


def test_cierra_consultas_que_superan_el_timeout(semantic_database) -> None:
    instance = SQLiteAdapter(semantic_database, timeout_ms=100)
    try:
        with pytest.raises(QueryTimeoutError):
            instance.execute(
                """
                WITH RECURSIVE c(x) AS (SELECT 1 UNION ALL SELECT x + 1 FROM c)
                SELECT COUNT(*) FROM c
                """
            )
    finally:
        instance.close()


def test_base_inexistente_falla_con_mensaje_seguro(tmp_path) -> None:
    instance = SQLiteAdapter(tmp_path / "no-existe.sqlite")
    try:
        with pytest.raises(DatabaseError, match="No existe la base"):
            instance.execute("SELECT * FROM personas")
    finally:
        instance.close()


def test_expone_metadatos_y_vistas(adapter) -> None:
    views = adapter.views()
    columns = adapter.describe_table("personas")

    assert [view["view"] for view in views] == ["hogares", "personas"]
    assert len(columns) == 26
    assert columns[0]["column"] == "codusu"


def test_el_authorizer_bloquea_load_extension() -> None:
    import sqlite3 as sqlite_module

    from eph_agent.database.sqlite import _authorizer

    assert (
        _authorizer(
            sqlite_module.SQLITE_FUNCTION,
            "load_extension",
            "load_extension",
            None,
            None,
        )
        == sqlite_module.SQLITE_DENY
    )
