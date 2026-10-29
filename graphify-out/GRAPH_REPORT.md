# Graph Report - Trabajo Final Diplomatura  (2026-10-29)

## Corpus Check
- 36 files · ~18,829 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 2, .example 1, .zip 1)

## Summary
- 372 nodes · 721 edges · 17 communities (10 shown, 7 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 82 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b753b30d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Evaluación y reproducibilidad
- Capa semántica EPH
- Lectura y tipado
- Carga y CLI
- Diseño de registros EPH 1T 2026
- pytest
- semantic.py
- Validación del período
- eph-agente
- bash
- Dependencia pandas 3.1.0
- api.py
- database/__init__.py
- test_api.py

## God Nodes (most connected - your core abstractions)
1. `bash` - 40 edges
2. `DatabaseSettings` - 21 edges
3. `SQLiteAdapter` - 20 edges
4. `DatabaseError` - 18 edges
5. `DatabaseAdapter` - 18 edges
6. `PostgresAdapter` - 16 edges
7. `Natural Language Query Agent on EPH` - 15 edges
8. `validate_query()` - 14 edges
9. `QueryResult` - 13 edges
10. `validate_dictionary()` - 13 edges

## Surprising Connections (you probably didn't know these)
- `Diccionario de metadatos de columnas` --references--> `Ponderadores de ingresos PONDII PONDIIO PONDIH`  [INFERRED]
  README.md → datos_indec/EPH_registro_1T2026.pdf
- `Vistas legibles personas y hogares` --references--> `Códigos especiales y no respuesta`  [INFERRED]
  README.md → datos_indec/EPH_registro_1T2026.pdf
- `Vistas legibles personas y hogares` --references--> `Identificadores CODUSU NRO_HOGAR COMPONENTE`  [INFERRED]
  README.md → datos_indec/EPH_registro_1T2026.pdf
- `Golden set de preguntas EPH` --conceptually_related_to--> `No comparabilidad estricta antes y después de 1T 2019`  [INFERRED]
  README.md → datos_indec/EPH_nota_metodologica_1_trim_2019.pdf
- `Agente de consultas en lenguaje natural sobre la EPH` --conceptually_related_to--> `Umbrales de calidad para publicar resultados`  [INFERRED]
  README.md → datos_indec/EPH_consideraciones_metodologicas_2t20.pdf

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Architecture of Natural Language Query Agent on EPH** — agente_de_consultas_en_lenguaje_natural_sobre_la_eph_architecture, agente_de_consultas_en_lenguaje_natural_sobre_la_eph, agente_de_consultas_en_lenguaje_natural_sobre_la_eph_tests [EXTRACTED 0.75]
- **Data for Natural Language Query Agent on EPH** — agente_de_consultas_en_lenguaje_natural_sobre_la_eph_data, agente_de_consultas_en_lenguaje_natural_sobre_la_eph, agente_de_consultas_en_lenguaje_natural_sobre_la_eph_tests [EXTRACTED 0.75]
- **Metrics for Natural Language Query Agent on EPH** — agente_de_consultas_en_lenguaje_natural_sobre_la_eph_metrics, agente_de_consultas_en_lenguaje_natural_sobre_la_eph, agente_de_consultas_en_lenguaje_natural_sobre_la_eph_tests [EXTRACTED 0.75]
- **Acceso semántico seguro a la EPH** — readme_readable_views, readme_metadata_dictionary, readme_describir_tabla, readme_ejecutar_sql, readme_safe_sql_execution [EXTRACTED 1.00]
- **Ponderación y calidad de estimaciones EPH** — datos_indec_eph_registro_1t2026_general_weight, datos_indec_eph_registro_1t2026_income_weights, datos_indec_eph_consideraciones_metodologicas_2t20_propensity_score, datos_indec_eph_consideraciones_metodologicas_2t20_calibration, datos_indec_eph_consideraciones_metodologicas_2t20_quality_thresholds [INFERRED 0.85]

## Communities (17 total, 7 thin omitted)

### Community 0 - "Evaluación y reproducibilidad"
Cohesion: 0.09
Nodes (21): buscar_zip(), construir_base(), convertir_tipos(), extraer_tablas(), leer_txt(), main(), tipo_sql(), validar_periodo() (+13 more)

### Community 1 - "Capa semántica EPH"
Cohesion: 0.11
Nodes (11): get_settings(), DatabaseBackend, DatabaseSettings, create_database_adapter(), test_accepts_cloudflare_d1_identifier(), test_accepts_postgresql_connection_string(), test_default_sqlite_path_is_relative_to_project(), test_defaults_to_local_sqlite() (+3 more)

### Community 2 - "Lectura y tipado"
Cohesion: 0.11
Nodes (19): agent, build, plan, permission, instructions, permission, edit, external_directory (+11 more)

### Community 3 - "Carga y CLI"
Cohesion: 0.12
Nodes (16): Natural Language Query Agent on EPH, Architecture of Natural Language Query Agent on EPH, Decision Log for Natural Language Query Agent on EPH, Data for Natural Language Query Agent on EPH, Deployment of Natural Language Query Agent on EPH, Future Improvements for Natural Language Query Agent on EPH, Implementer for Natural Language Query Agent on EPH, Integrations for Natural Language Query Agent on EPH (+8 more)

### Community 4 - "Diseño de registros EPH 1T 2026"
Cohesion: 0.07
Nodes (27): Ajuste por calibración demográfica, Panel de rotación 2-2-2, Ajuste por propensity score, Umbrales de calidad para publicar resultados, Relevamiento telefónico EPH 2T 2020, Coeficientes de ajuste 2016-2018, Revisión de cobertura geográfica EPH, Ajuste de proyecciones de población (+19 more)

### Community 5 - "pytest"
Cohesion: 0.09
Nodes (19): _authorizer(), SQLiteAdapter, SQLGuardError, validate_query(), adapter(), test_acota_las_filas_devueltas(), test_base_inexistente_falla_con_mensaje_seguro(), test_cierra_consultas_que_superan_el_timeout() (+11 more)

### Community 6 - "semantic.py"
Cohesion: 0.10
Nodes (26): _check_column_values(), _check_dictionary_structure(), describe_table(), _from_json(), install_semantic_layer(), list_views(), load_dictionary(), main() (+18 more)

### Community 12 - "bash"
Cohesion: 0.05
Nodes (39): cat*, curl *, docker *, find*, git add*, git commit*, git diff*, git log* (+31 more)

### Community 14 - "api.py"
Cohesion: 0.11
Nodes (16): describe_table(), execute_sql(), get_adapter(), health(), schema(), DatabaseAdapter, ColumnMetadata, DescribeTableRequest (+8 more)

### Community 15 - "database/__init__.py"
Cohesion: 0.12
Nodes (6): DatabaseError, QueryExecutionError, QueryResult, QueryTimeoutError, D1Adapter, PostgresAdapter

## Knowledge Gaps
- **25 isolated node(s):** `eph-agente`, `Perfiles local dev y eval`, `Despliegue reproducible en contenedor`, `Condición de actividad ESTADO`, `Variables demográficas CH03-CH16` (+20 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 164 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DatabaseSettings` connect `Capa semántica EPH` to `api.py`, `database/__init__.py`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `DatabaseSettings` (e.g. with `get_adapter()` and `get_settings()`) actually correct?**
  _`DatabaseSettings` has 11 INFERRED edges - model-reasoned connections that need verification._
- **What connects `eph-agente`, `Perfiles local dev y eval`, `Despliegue reproducible en contenedor` to the rest of the system?**
  _25 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Evaluación y reproducibilidad` be split into smaller, more focused modules?**
  _Cohesion score 0.09042553191489362 - nodes in this community are weakly interconnected._
- **Why does `SQLiteAdapter` connect `pytest` to `Capa semántica EPH`, `database/__init__.py`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `SQLiteAdapter` (e.g. with `DatabaseError` and `QueryExecutionError`) actually correct?**
  _`SQLiteAdapter` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Should `Capa semántica EPH` be split into smaller, more focused modules?**
  _Cohesion score 0.10606060606060606 - nodes in this community are weakly interconnected._