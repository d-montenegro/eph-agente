# Graph Report - Trabajo Final Diplomatura  (2026-10-29)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 141 nodes · 206 edges · 14 communities (7 shown, 7 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 22 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `3ebcc82d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Evaluación y reproducibilidad
- Capa semántica EPH
- Lectura y tipado
- Carga y CLI
- Calidad metodológica
- Agente y herramientas
- Construcción SQLite
- Validación del período
- eph-agente
- Dependencia pandas 3.1.0

## God Nodes (most connected - your core abstractions)
1. `DatabaseSettings` - 15 edges
2. `Natural Language Query Agent on EPH` - 15 edges
3. `bash` - 10 edges
4. `construir_base()` - 9 edges
5. `DatabaseBackend` - 8 edges
6. `extraer_tablas()` - 7 edges
7. `leer_txt()` - 7 edges
8. `validar_periodo()` - 7 edges
9. `convertir_tipos()` - 6 edges
10. `main()` - 6 edges

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

## Communities (14 total, 7 thin omitted)

### Community 0 - "Evaluación y reproducibilidad"
Cohesion: 0.15
Nodes (13): buscar_zip(), construir_base(), convertir_tipos(), extraer_tablas(), leer_txt(), main(), tipo_sql(), validar_periodo() (+5 more)

### Community 1 - "Capa semántica EPH"
Cohesion: 0.12
Nodes (9): DatabaseBackend, DatabaseSettings, test_accepts_cloudflare_d1_identifier(), test_accepts_postgresql_connection_string(), test_default_sqlite_path_is_relative_to_project(), test_defaults_to_local_sqlite(), test_rejects_incompatible_backend_and_url(), test_resolves_absolute_sqlite_path() (+1 more)

### Community 2 - "Lectura y tipado"
Cohesion: 0.10
Nodes (22): agent, build, plan, git diff*, git log*, git status*, make check*, make test* (+14 more)

### Community 3 - "Carga y CLI"
Cohesion: 0.12
Nodes (16): Natural Language Query Agent on EPH, Architecture of Natural Language Query Agent on EPH, Decision Log for Natural Language Query Agent on EPH, Data for Natural Language Query Agent on EPH, Deployment of Natural Language Query Agent on EPH, Future Improvements for Natural Language Query Agent on EPH, Implementer for Natural Language Query Agent on EPH, Integrations for Natural Language Query Agent on EPH (+8 more)

### Community 4 - "Calidad metodológica"
Cohesion: 0.17
Nodes (13): Condición de actividad ESTADO, Variables demográficas CH03-CH16, Campos de ingresos P21 P47T ITF IPCF, Ponderadores de ingresos PONDII PONDIIO PONDIH, Códigos especiales y no respuesta, Diseño de registros EPH 1T 2026, Identificadores CODUSU NRO_HOGAR COMPONENTE, Herramienta describir_tabla (+5 more)

### Community 5 - "Agente y herramientas"
Cohesion: 0.22
Nodes (7): Coeficientes de ajuste 2016-2018, Revisión de cobertura geográfica EPH, Ajuste de proyecciones de población, Archivos originales del INDEC, Golden set de preguntas EPH, Perfiles local dev y eval, Despliegue reproducible en contenedor

### Community 6 - "Construcción SQLite"
Cohesion: 0.29
Nodes (7): Ajuste por calibración demográfica, Panel de rotación 2-2-2, Ajuste por propensity score, Umbrales de calidad para publicar resultados, Relevamiento telefónico EPH 2T 2020, Ponderador general PONDERA, Agente de consultas en lenguaje natural sobre la EPH

## Knowledge Gaps
- **25 isolated node(s):** `eph-agente`, `Perfiles local dev y eval`, `Despliegue reproducible en contenedor`, `Condición de actividad ESTADO`, `Variables demográficas CH03-CH16` (+20 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 67 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Diseño de registros EPH 1T 2026` connect `Calidad metodológica` to `Agente y herramientas`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `DatabaseSettings` (e.g. with `test_accepts_cloudflare_d1_identifier()` and `test_accepts_postgresql_connection_string()`) actually correct?**
  _`DatabaseSettings` has 7 INFERRED edges - model-reasoned connections that need verification._
- **What connects `eph-agente`, `Perfiles local dev y eval`, `Despliegue reproducible en contenedor` to the rest of the system?**
  _25 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Evaluación y reproducibilidad` be split into smaller, more focused modules?**
  _Cohesion score 0.14623655913978495 - nodes in this community are weakly interconnected._
- **Why does `Archivos originales del INDEC` connect `Agente y herramientas` to `Calidad metodológica`, `Construcción SQLite`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `construir_base()` (e.g. with `test_construir_base_creates_tables_and_indexes()` and `test_reconstruye_el_1t2026_con_los_conteos_oficiales()`) actually correct?**
  _`construir_base()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Should `Capa semántica EPH` be split into smaller, more focused modules?**
  _Cohesion score 0.11724137931034483 - nodes in this community are weakly interconnected._