# Código fuente

| Archivo | Qué hace |
| --- | --- |
| `eph_a_sqlite.py` | Construye la base de datos con los microdatos de la EPH del 1T 2026 que están en `datos_indec/`. |
| `requirements.txt` | Dependencias de Python. |

## Requisitos

- Python 3.10 o superior.
- El zip de microdatos del 1T 2026 en la carpeta `datos_indec/` (ver [datos_indec/README.md](../datos_indec/README.md)).

## Crear el entorno virtual

Desde la raíz del repositorio:

```bash
python3 -m venv .venv
source .venv/bin/activate          # en Windows: .venv\Scripts\activate
pip install -r src/requirements.txt
```

## Crear la base de datos

Con el entorno virtual activado, desde la raíz del repositorio:

```bash
python src/eph_a_sqlite.py
```

El script lee el zip de `datos_indec/` y genera `eph.sqlite` en la raíz del repositorio. Cada corrida reconstruye la base desde cero. La base no se versiona: se regenera con este comando.

Opciones:

```bash
python src/eph_a_sqlite.py --db otra_ruta.sqlite    # generar la base en otro lugar
python src/eph_a_sqlite.py --zip otro/archivo.zip   # usar un zip que no está en datos_indec/
```

Al terminar, el script muestra cuántas filas y columnas cargó en cada tabla (`individual` y `hogar`).
