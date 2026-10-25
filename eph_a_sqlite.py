#!/usr/bin/env python3
"""
Construye la base de datos del agente EPH a partir de los microdatos del INDEC.

Alcance inicial: un único trimestre de la EPH continua, el primero de 2026 (1T 2026),
el último publicado al momento de implementar esto. Incorporar otros trimestres es una
mejora futura: cada uno requiere antes un análisis de cambios en el diseño de registros.

La base se reconstruye siempre con el mismo proceso: cada corrida borra las tablas y
las vuelve a crear desde el zip del INDEC. Las tablas quedan tal como las publica el
INDEC (mismas columnas y códigos); la capa semántica (vistas legibles y metadatos)
se construye después, sobre ellas.

Uso:
    pip install pandas requests
    python eph_a_sqlite.py                        # descarga el 1T 2026 y construye eph.sqlite
    python eph_a_sqlite.py --zip archivo.zip      # usa un zip ya descargado a mano

Tablas resultantes:
    individual  -> una fila por persona encuestada (usu_individual_*.txt)
    hogar       -> una fila por hogar encuestado   (usu_hogar_*.txt)
    cargas      -> período cargado, origen del zip y fecha de carga

Fuentes:
    Bases de datos: https://www.indec.gob.ar/indec/web/Institucional-Indec-BasesDeDatos
    Diseño de registros 1T 2026:
        https://www.indec.gob.ar/ftp/cuadros/menusuperior/eph/EPH_registro_1T2026.pdf
"""

from __future__ import annotations

import argparse
import datetime as dt
import io
import sqlite3
import sys
import zipfile
from pathlib import Path

import pandas as pd
import requests

# Período del alcance inicial.
ANIO, TRIMESTRE = 2026, 1

BASE_URL = "https://www.indec.gob.ar/ftp/cuadros/menusuperior/eph/"
HEADERS = {"User-Agent": "Mozilla/5.0 (eph_a_sqlite.py; uso personal)"}
TABLAS = ("individual", "hogar")


# ----------------------------------------------------------------------------
# Descarga
# ----------------------------------------------------------------------------

def urls_candidatas(anio: int, trim: int) -> list[str]:
    """INDEC no fue consistente con los nombres de archivo; probamos variantes."""
    ordinal = {1: "1er", 2: "2do", 3: "3er", 4: "4to"}[trim]
    nombres = [
        f"EPH_usu_{ordinal}_Trim_{anio}_txt.zip",
        f"EPH_usu_{trim}_Trim_{anio}_txt.zip",
        f"EPH_usu_{ordinal}Trim_{anio}_txt.zip",
        f"EPH_usu_{ordinal}_trim_{anio}_txt.zip",
        f"EPH_usu_{trim}_trim_{anio}_txt.zip",
    ]
    return [BASE_URL + n for n in dict.fromkeys(nombres)]


def descargar(anio: int, trim: int, cache: Path) -> tuple[Path, str]:
    """Devuelve (ruta_zip, origen). Reutiliza el zip si ya está descargado."""
    cache.mkdir(parents=True, exist_ok=True)
    destino = cache / f"eph_{anio}T{trim}.zip"
    if destino.exists() and zipfile.is_zipfile(destino):
        return destino, f"cache ({destino})"

    with requests.Session() as sesion:
        sesion.headers.update(HEADERS)
        for url in urls_candidatas(anio, trim):
            try:
                r = sesion.get(url, timeout=60)
            except requests.RequestException as e:
                print(f"  ! error de red con {url}: {e}")
                continue
            if r.status_code == 200 and r.content[:2] == b"PK":
                destino.write_bytes(r.content)
                return destino, url

    sys.exit(
        f"No encontré el zip de {anio}T{trim} en INDEC. Bajalo a mano desde la página de "
        "Bases de datos y corré: python eph_a_sqlite.py --zip <archivo.zip>"
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


def construir_base(db: Path, tablas: dict[str, pd.DataFrame], origen: str) -> None:
    con = sqlite3.connect(db)
    try:
        with con:  # transacción: o queda la base completa o no cambia nada
            # Se eliminan vistas y tablas previas para reconstruir desde cero.
            for (vista,) in con.execute("SELECT name FROM sqlite_master WHERE type='view'").fetchall():
                con.execute(f'DROP VIEW "{vista}"')
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

            con.execute(
                "CREATE TABLE cargas (anio INTEGER, trimestre INTEGER, tabla TEXT, "
                "filas INTEGER, origen TEXT, cargado_en TEXT)"
            )
            ahora = dt.datetime.now().isoformat(timespec="seconds")
            con.executemany(
                "INSERT INTO cargas VALUES (?,?,?,?,?,?)",
                [(ANIO, TRIMESTRE, n, len(df), origen, ahora) for n, df in tablas.items()],
            )

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
    p.add_argument("--db", type=Path, default=Path("eph.sqlite"), help="archivo de la base (default: eph.sqlite)")
    p.add_argument("--cache", type=Path, default=Path("eph_zips"), help="carpeta de los zip (default: eph_zips)")
    p.add_argument("--zip", type=Path, help="usar un zip ya descargado en lugar de bajarlo")
    args = p.parse_args()

    if args.zip:
        ruta, origen = args.zip, str(args.zip)
    else:
        print(f"> Descargando {ANIO}T{TRIMESTRE}...")
        ruta, origen = descargar(ANIO, TRIMESTRE, args.cache)
    print(f"> Leyendo {ruta}")
    tablas = extraer_tablas(ruta)
    validar_periodo(tablas)

    print(f"> Construyendo {args.db}")
    construir_base(args.db, tablas, origen)
    for nombre, df in tablas.items():
        print(f"  {nombre}: {len(df):,} filas, {df.shape[1]} columnas")
    print(f"\nListo: {args.db.resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
