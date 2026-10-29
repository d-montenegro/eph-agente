import pytest

from eph_agent.sql_guard import SQLGuardError, validate_query


def test_acepta_lectura_sobre_vistas() -> None:
    guarded = validate_query("SELECT sexo, COUNT(*) FROM personas GROUP BY sexo")

    assert guarded.startswith("SELECT * FROM (")
    assert "LIMIT 1000" in guarded


def test_acepta_cte_y_join_entre_vistas() -> None:
    guarded = validate_query(
        """
        WITH activos AS (SELECT * FROM personas WHERE estado_actividad = 'Ocupado')
        SELECT COUNT(*) FROM activos a JOIN hogares h USING (codusu, nro_hogar)
        """
    )

    assert "WITH activos" in guarded
    assert "LIMIT 1000" in guarded


def test_acepta_select_sin_tablas() -> None:
    assert "LIMIT 1000" in validate_query("SELECT 1")


def test_aplica_el_limite_configurado() -> None:
    assert "LIMIT 25" in validate_query("SELECT * FROM personas", row_limit=25)


@pytest.mark.parametrize(
    ("sql", "mensaje"),
    [
        ("SELECT * FROM individual", "Solo se pueden consultar las vistas"),
        ("SELECT * FROM main.personas", "nombres calificados"),
        ("SELECT 1; SELECT 2", "una única sentencia"),
        ("INSERT INTO personas VALUES (1)", "SELECT"),
        ("UPDATE personas SET sexo = 'X'", "SELECT"),
        ("DELETE FROM personas", "SELECT"),
        ("DROP TABLE individual", "SELECT"),
        ("CREATE TABLE x (a int)", "SELECT"),
        ("PRAGMA query_only = OFF", "SELECT"),
        ("ATTACH DATABASE 'x' AS y", "SELECT"),
        ("SELECT * FROM personas WHERE codusu = ?", "no admite parámetros"),
        ("", "vacía"),
    ],
)
def test_rechaza_consultas_peligrosas(sql: str, mensaje: str) -> None:
    with pytest.raises(SQLGuardError, match=mensaje):
        validate_query(sql)


def test_rechaza_dml_escondido_en_cte() -> None:
    with pytest.raises(SQLGuardError):
        validate_query("WITH x AS (SELECT 1) DELETE FROM personas")
