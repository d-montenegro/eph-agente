import sqlite3
from pathlib import Path

import pandas as pd
import pytest

from eph_a_sqlite import construir_base, convertir_tipos, extraer_tablas, validar_periodo

RAIZ_REPO = Path(__file__).resolve().parents[1]
ZIP_1T2026 = RAIZ_REPO / "datos_indec" / "EPH_usu_1_Trim_2026_txt.zip"


def test_convertir_tipos_preserves_identifiers_and_converts_numbers() -> None:
    frame = pd.DataFrame(
        {
            "CODUSU": ["001", "002"],
            "CNO_COD": ["0001", "0002"],
            "INGRESO": ["10,5", ""],
            "ETIQUETA": ["Ocupado", "Desocupado"],
        }
    )

    result = convertir_tipos(frame)

    assert result["CODUSU"].tolist() == ["001", "002"]
    assert result["CNO_COD"].tolist() == ["0001", "0002"]
    assert result["INGRESO"].iloc[0] == 10.5
    assert pd.isna(result["INGRESO"].iloc[1])


def test_validar_periodo_rejects_another_quarter() -> None:
    tables = {"individual": pd.DataFrame({"ANO4": [2026], "TRIMESTRE": [2]})}

    with pytest.raises(SystemExit, match="alcance es solo"):
        validar_periodo(tables)


def test_construir_base_creates_tables_and_indexes(tmp_path) -> None:
    tables = {
        "individual": pd.DataFrame(
            {"CODUSU": ["A"], "NRO_HOGAR": [1], "AGLOMERADO": [13], "VALOR": [2]}
        ),
        "hogar": pd.DataFrame(
            {"CODUSU": ["A"], "NRO_HOGAR": [1], "AGLOMERADO": [13], "VALOR": [3]}
        ),
    }
    database = tmp_path / "eph.sqlite"

    construir_base(database, tables)

    with sqlite3.connect(database) as connection:
        tables_found = {
            row[0]
            for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        }
        indexes_found = {
            row[0]
            for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'index'")
        }

    assert tables_found == {"individual", "hogar"}
    assert {
        "ix_individual_hogar",
        "ix_individual_aglo",
        "ix_hogar_hogar",
        "ix_hogar_aglo",
    }.issubset(indexes_found)


@pytest.mark.skipif(not ZIP_1T2026.exists(), reason="falta el zip versionado del 1T 2026")
def test_reconstruye_el_1t2026_con_los_conteos_oficiales(tmp_path) -> None:
    tablas = extraer_tablas(ZIP_1T2026)
    validar_periodo(tablas)
    database = tmp_path / "eph.sqlite"

    construir_base(database, tablas)

    with sqlite3.connect(database) as connection:
        tablas_crudas = {
            row[0]
            for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        }
        filas_hogar = connection.execute("SELECT COUNT(*) FROM hogar").fetchone()[0]
        filas_individual = connection.execute("SELECT COUNT(*) FROM individual").fetchone()[0]
        columnas_hogar = len(connection.execute("PRAGMA table_info(hogar)").fetchall())
        columnas_individual = len(connection.execute("PRAGMA table_info(individual)").fetchall())

    assert tablas_crudas == {"hogar", "individual"}
    assert (filas_hogar, columnas_hogar) == (15_447, 98)
    assert (filas_individual, columnas_individual) == (43_739, 234)
