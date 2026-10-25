# Datos del INDEC

Esta carpeta guarda los archivos originales del INDEC que usa el proyecto, tal como se descargan, para que cualquiera pueda reconstruir la base sin depender de la web del INDEC.

## Alcance

Encuesta Permanente de Hogares (EPH) continua, **1er trimestre de 2026** (1T 2026), el último publicado al momento de implementar el proyecto.

## Archivos

| Archivo | Qué es |
| --- | --- |
| Zip de microdatos del 1T 2026 (formato txt) | Bases usuarias Individual y Hogar. Es lo que carga `src/eph_a_sqlite.py`. |
| `EPH_registro_1T2026.pdf` | Diseño de registros y estructura para las bases preliminares Hogar y Personas: describe cada variable y sus códigos. |

## De dónde se descargan

- **Microdatos:** [INDEC – Bases de datos](https://www.indec.gob.ar/indec/web/Institucional-Indec-BasesDeDatos), sección *Encuesta Permanente de Hogares (EPH)* → *Microdatos y documentos 2016-2026* → 1er trimestre de 2026, base en formato txt.
- **Diseño de registros:** [EPH_registro_1T2026.pdf](https://www.indec.gob.ar/ftp/cuadros/menusuperior/eph/EPH_registro_1T2026.pdf), publicado en agosto de 2026, en la misma página.

Los archivos se guardan sin modificar y con el nombre original del INDEC.

## Cita

Según la política de difusión del INDEC, toda publicación basada en estos microdatos debe citar la fuente: *"Fuente: Instituto Nacional de Estadística y Censos (INDEC)."*
