import shutil
import sqlite3
from pathlib import Path

import pytest

from eph_a_sqlite import construir_base, extraer_tablas, validar_periodo
from eph_agent.semantic import install_semantic_layer

RAIZ_REPO = Path(__file__).resolve().parents[1]
ZIP_1T2026 = RAIZ_REPO / "datos_indec" / "EPH_usu_1_Trim_2026_txt.zip"


@pytest.fixture(scope="session")
def eph_raw_database(tmp_path_factory) -> Path:
    if not ZIP_1T2026.exists():
        pytest.skip("falta el zip versionado del 1T 2026")
    tablas = extraer_tablas(ZIP_1T2026)
    validar_periodo(tablas)
    database = tmp_path_factory.mktemp("eph") / "eph.sqlite"
    construir_base(database, tablas)
    return database


@pytest.fixture()
def eph_connection(eph_raw_database: Path):
    connection = sqlite3.connect(eph_raw_database)
    try:
        yield connection
    finally:
        connection.close()


@pytest.fixture()
def semantic_database(eph_raw_database: Path, tmp_path) -> Path:
    database = tmp_path / "semantic.sqlite"
    shutil.copyfile(eph_raw_database, database)
    connection = sqlite3.connect(database)
    try:
        install_semantic_layer(connection)
    finally:
        connection.close()
    return database


@pytest.fixture()
def semantic_connection(semantic_database: Path):
    connection = sqlite3.connect(semantic_database)
    try:
        yield connection
    finally:
        connection.close()
