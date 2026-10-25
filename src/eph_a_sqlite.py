#!/usr/bin/env python3
"""
Construye la base de datos del agente EPH a partir de los microdatos del INDEC.

Alcance inicial: un único trimestre de la EPH continua, el primero de 2026 (1T 2026),
el último publicado al momento de implementar esto. Incorporar otros trimestres es una
mejora futura: cada uno requiere antes un análisis de cambios en el diseño de registros.

Los datos se leen del zip original del INDEC guardado en la carpeta datos_indec/ del
repositorio (ver datos_indec/README.md para saber de dónde se descarga). La base se
genera en la raíz del repositorio (eph.sqlite). Ver src/README.md para instalar y correr.

La base se reconstruye siempre con el mismo proceso: cada corrida borra las tablas y
las vuelve a crear desde el zip. Las tablas quedan tal como las publica el INDEC
(mismas columnas y códigos); la capa semántica (vistas legibles y metadatos) se
construye después, sobre ellas.

Uso (desde la raíz del repositorio, con el entorno virtual activado):
    python src/eph_a_sqlite.py                        # usa el zip de datos_indec/ y construye eph.sqlite
    python src/eph_a_sqlite.py --zip otro/archivo.zip # usa un zip de otra ubicación

Tablas resultantes:
    individual  -> una fila por persona encuestada (usu_individual_*.txt)
    hogar       -> una fila por hogar encuestado   (usu_hogar_*.txt)

Fuentes:
    Bases de datos: https://www.indec.gob.ar/indec/web/Institucional-Indec-BasesDeDatos
    Diseño de registros 1T 2026:
        https://www.indec.gob.ar/ftp/cuadros/menusuperior/eph/EPH_registro_1T2026.pdf
"""

from __future__ import annotations

import argparse
import io
import sqlite3
import sys
import zipfile
from pathlib import Path

import pandas as pd

# Período del alcance inicial.
ANIO, TRIMESTRE = 2026, 1

RAIZ_REPO = Path(__file__).resolve().parent.parent
CARPETA_DATOS = RAIZ_REPO / "datos_indec"
BASE_DEFAULT = RAIZ_REPO / "eph.sqlite"
TABLAS = ("individual", "hogar")


# ----------------------------------------------------------------------------
# Ubicación del zip
# ----------------------------------------------------------------------------

def buscar_zip(carpeta: Path) -> Path:
    """Devuelve el único zip de microdatos que hay en la carpeta de datos del INDEC."""
    zips = sorted(p for p in carpeta.glob("*.zip") if zipfile.is_zipfile(p))
    if len(zips) == 1:
        return zips[0]
    if not zips:
        motivo = f"No hay ningún zip en {carpeta}."
    else:
        motivo = f"Hay más de un zip en {carpeta}: {', '.join(p.name for p in zips)}."
    sys.exit(
        f"{motivo} Dejá ahí solo el zip de microdatos del {TRIMESTRE}T {ANIO} "
        f"(ver {carpeta / 'README.md'}) o indicá uno con --zip."
    )


# ----------------------------------------------------------------------------
# Lectura del zip
# ----------------------------------------------------------------------------

def leer_txt(zf: zipfile.ZipFile, nombre: str) -> pd.DataFrame:
    crudo = zf.read(nombre)
    try:
        texto = crudo.decode("utf-8")
    except UnicodeDecodeError:
        texto = crudo.decode("latin-1")
    # Se lee todo como texto y se convierte después (el INDEC usa coma decimal).
    df = pd.read_csv(io.StringIO(texto), sep=";", dtype=str, keep_default_na=False)
    df.columns = [c.strip().upper().lstrip("﻿") for c in df.columns]
    return convertir_tipos(df)


def convertir_tipos(df: pd.DataFrame) -> pd.DataFrame:
    """Convierte a número las columnas 100% numéricas. Los valores no cambian:
    los códigos especiales del INDEC (-9, 0, etc.) se conservan tal cual."""
    for col in df.columns:
        s = df[col].str.strip()
        vacios = s.eq("")
        if col == "CODUSU" or col.endswith("_COD"):
            # Identificadores y códigos de clasificación (CNO, CAES): siempre texto,
            # para no perder ceros a la izquierda.
            df[col] = s.where(~vacios, None)
            continue
        num = pd.to_numeric(s.str.replace(",", ".", regex=False), errors="coerce")
        if num[~vacios].notna().all():
            num[vacios] = pd.NA
            df[col] = num.astype("Int64" if (num.dropna() % 1 == 0).all() else "Float64")
        else:
            df[col] = s.where(~vacios, None)
    return df


def extraer_tablas(ruta_zip: Path) -> dict[str, pd.DataFrame]:
    tablas: dict[str, pd.DataFrame] = {}
    with zipfile.ZipFile(ruta_zip) as zf:
        for nombre in zf.namelist():
            base = Path(nombre).name.lower()
            if base.endswith(".txt"):
                for tabla in TABLAS:
                    if tabla in base:
                        tablas[tabla] = leer_txt(zf, nombre)
    faltan = [t for t in TABLAS if t not in tablas]
    if faltan:
        sys.exit(f"El zip {ruta_zip} no tiene las bases: {', '.join(faltan)}")
    return tablas


def validar_periodo(tablas: dict[str, pd.DataFrame]) -> None:
    """Verifica que el zip corresponda al período del alcance."""
    for nombre, df in tablas.items():
        periodos = set(map(tuple, df[["ANO4", "TRIMESTRE"]].drop_duplicates().to_numpy().tolist()))
        if periodos != {(ANIO, TRIMESTRE)}:
            sys.exit(
                f"La base {nombre} trae los períodos {sorted(periodos)}, "
                f"pero el alcance es solo {ANIO}T{TRIMESTRE}."
            )


# ----------------------------------------------------------------------------
# Base de datos
# ----------------------------------------------------------------------------

def tipo_sql(serie: pd.Series) -> str:
    if pd.api.types.is_integer_dtype(serie):
        return "INTEGER"
    if pd.api.types.is_float_dtype(serie):
        return "REAL"
    return "TEXT"


def construir_base(db: Path, tablas: dict[str, pd.DataFrame]) -> None:
    con = sqlite3.connect(db)
    try:
        with con:  # transacción: o queda la base completa o no cambia nada
            # Se eliminan vistas y tablas previas para reconstruir desde cero.
            for (vista,) in con.execute("SELECT name FROM sqlite_master WHERE type='view'").fetchall():
                con.execute(f'DROP VIEW "{vista}"')
            # "cargas" es una tabla de versiones anteriores del script.
            for tabla in (*TABLAS, "cargas"):
                con.execute(f'DROP TABLE IF EXISTS "{tabla}"')

            for nombre, df in tablas.items():
                defs = ", ".join(f'"{c}" {tipo_sql(df[c])}' for c in df.columns)
                con.execute(f'CREATE TABLE "{nombre}" ({defs})')
                cols = ", ".join(f'"{c}"' for c in df.columns)
                marcas = ", ".join("?" for _ in df.columns)
                filas = (
                    tuple(None if pd.isna(v) else (v.item() if hasattr(v, "item") else v) for v in fila)
                    for fila in df.itertuples(index=False, name=None)
                )
                con.executemany(f'INSERT INTO "{nombre}" ({cols}) VALUES ({marcas})', filas)

            for tabla in TABLAS:
                con.execute(f'CREATE INDEX ix_{tabla}_hogar ON "{tabla}" (CODUSU, NRO_HOGAR)')
                con.execute(f'CREATE INDEX ix_{tabla}_aglo ON "{tabla}" (AGLOMERADO)')
        con.execute("VACUUM")
    finally:
        con.close()


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------

def main() -> int:
    p = argparse.ArgumentParser(
        description=f"Construye la base del agente EPH con el {ANIO}T{TRIMESTRE} del INDEC."
    )
    p.add_argument("--db", type=Path, default=BASE_DEFAULT, help="archivo de la base (default: eph.sqlite en la raíz del repo)")
    p.add_argument("--zip", type=Path, help="zip de microdatos (default: el que esté en datos_indec/)")
    args = p.parse_args()

    ruta = args.zip or buscar_zip(CARPETA_DATOS)
    print(f"> Leyendo {ruta}")
    tablas = extraer_tablas(ruta)
    validar_periodo(tablas)

    print(f"> Construyendo {args.db}")
    construir_base(args.db, tablas)
    for nombre, df in tablas.items():
        print(f"  {nombre}: {len(df):,} filas, {df.shape[1]} columnas")
    print(f"\nListo: {args.db.resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
