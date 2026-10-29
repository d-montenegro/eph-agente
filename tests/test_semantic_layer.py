import copy

import pytest

from eph_agent.profile import profile_view
from eph_agent.semantic import (
    SemanticLayerError,
    describe_table,
    install_semantic_layer,
    list_views,
    load_dictionary,
    validate_dictionary,
)


def count(connection, sql):
    return connection.execute(sql).fetchone()[0]


def test_instala_las_dos_vistas_con_todas_las_filas(semantic_connection) -> None:
    views = list_views(semantic_connection)

    assert [view["view"] for view in views] == ["hogares", "personas"]
    assert all(view["period"] == {"anio": 2026, "trimestre": 1} for view in views)
    assert count(semantic_connection, "SELECT COUNT(*) FROM personas") == 43_739
    assert count(semantic_connection, "SELECT COUNT(*) FROM hogares") == 15_447


def test_traduce_codigos_a_etiquetas_legibles(semantic_connection) -> None:
    sexos = {row[0] for row in semantic_connection.execute("SELECT DISTINCT sexo FROM personas")}
    estados = {
        row[0]
        for row in semantic_connection.execute(
            "SELECT DISTINCT estado_actividad FROM personas WHERE estado_actividad IS NOT NULL"
        )
    }

    assert sexos == {"Varón", "Mujer"}
    assert estados == {"Ocupado", "Desocupado", "Inactivo", "Menor de 10 años"}


def test_edad_convierte_codigos_especiales_a_null(semantic_connection) -> None:
    edades_nulas = count(semantic_connection, "SELECT COUNT(*) FROM personas WHERE edad IS NULL")
    grupos_nulos = count(
        semantic_connection, "SELECT COUNT(*) FROM personas WHERE grupo_edad IS NULL"
    )

    assert edades_nulas == 290
    assert grupos_nulos == 290
    assert count(semantic_connection, "SELECT COUNT(*) FROM personas WHERE edad = 99") == 0


def test_entrevista_no_realizada_queda_sin_estado(semantic_connection) -> None:
    assert (
        count(
            semantic_connection,
            "SELECT COUNT(*) FROM personas WHERE estado_actividad IS NULL",
        )
        == 86
    )


def test_ingreso_laboral_solo_existe_para_ocupados(semantic_connection) -> None:
    fuera_de_universo = count(
        semantic_connection,
        """
        SELECT COUNT(*) FROM personas
        WHERE estado_actividad <> 'Ocupado' AND ingreso_ocupacion_principal IS NOT NULL
        """,
    )
    no_respuesta = count(
        semantic_connection,
        """
        SELECT COUNT(*) FROM personas
        WHERE estado_actividad = 'Ocupado' AND ingreso_ocupacion_principal IS NULL
        """,
    )
    cero_valido = count(
        semantic_connection,
        """
        SELECT COUNT(*) FROM personas
        WHERE estado_actividad = 'Ocupado' AND ingreso_ocupacion_principal = 0
        """,
    )

    assert fuera_de_universo == 0
    assert no_respuesta == 3_726
    assert cero_valido == 399


def test_categoria_ocupacional_fuera_de_universo_es_null(semantic_connection) -> None:
    assert (
        count(
            semantic_connection,
            "SELECT COUNT(*) FROM personas WHERE categoria_ocupacion IS NOT NULL",
        )
        == 20_616
    )


def test_personas_y_hogares_se_unen_por_identificadores_documentados(semantic_connection) -> None:
    unidas = count(
        semantic_connection,
        "SELECT COUNT(*) FROM personas p JOIN hogares h USING (codusu, nro_hogar)",
    )
    hogares_distintos = count(
        semantic_connection,
        "SELECT COUNT(*) FROM (SELECT DISTINCT codusu, nro_hogar FROM personas)",
    )

    assert unidas == 43_739
    assert hogares_distintos == 15_447


def test_metadatos_describen_todas_las_columnas(semantic_connection) -> None:
    personas = describe_table(semantic_connection, "personas")
    sexo = next(column for column in personas if column["column"] == "sexo")

    assert len(personas) == 26
    assert sexo["possible_values"] == ["Varón", "Mujer"]
    assert sexo["type"] == "categorica"
    assert sexo["universe"] == "Todas las personas."
    assert "género" in sexo["synonyms"]


def test_validacion_acepta_diccionario_y_datos(semantic_connection) -> None:
    validate_dictionary(semantic_connection)


def test_validacion_falla_con_valor_no_documentado(semantic_connection) -> None:
    dictionary = copy.deepcopy(load_dictionary())
    dictionary["views"]["personas"]["columns"]["sexo"]["possible_values"] = ["Varón"]

    with pytest.raises(SemanticLayerError, match="valores no documentados"):
        validate_dictionary(semantic_connection, dictionary)


def test_validacion_falla_con_columna_cruda_inexistente(semantic_connection) -> None:
    dictionary = copy.deepcopy(load_dictionary())
    dictionary["views"]["personas"]["columns"]["sexo"]["source"] = "NO_EXISTE"

    with pytest.raises(SemanticLayerError, match="falta la columna cruda NO_EXISTE"):
        validate_dictionary(semantic_connection, dictionary)


def test_instalacion_es_idempotente(semantic_connection) -> None:
    install_semantic_layer(semantic_connection)

    assert count(semantic_connection, "SELECT COUNT(*) FROM semantic_views") == 2
    assert count(semantic_connection, "SELECT COUNT(*) FROM semantic_columns") == 37


def test_profiling_resume_nulos_rangos_y_valores(semantic_connection) -> None:
    profile = profile_view(semantic_connection, "personas")

    assert profile["rows"] == 43_739
    assert profile["columns"]["edad"]["kind"] == "numeric"
    assert profile["columns"]["edad"]["nulls"] == 290
    assert profile["columns"]["sexo"]["kind"] == "categorical"
    assert profile["columns"]["sexo"]["values"] == {"Varón": 20_970, "Mujer": 22_769}


def test_profiling_rechaza_nombres_inseguros(semantic_connection) -> None:
    with pytest.raises(ValueError, match="inválido"):
        profile_view(semantic_connection, "personas; DROP TABLE individual")
