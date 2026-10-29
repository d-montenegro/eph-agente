# Graph Report - Trabajo Final Diplomatura  (2026-10-29)

## Corpus Check
- 49 files · ~24,263 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 2, .example 1, .zip 1)

## Summary
- 568 nodes · 1278 edges · 22 communities (15 shown, 7 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 160 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `44c1e3f1`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Evaluación y reproducibilidad
- Capa semántica EPH
- opencode.json
- Carga y CLI
- Diseño de registros EPH 1T 2026
- pytest
- semantic.py
- Validación del período
- eph-agente
- bash
- Dependencia pandas 3.1.0
- api.py
- agent.py
- test_api.py
- providers/__init__.py
- test_providers.py
- test_api_agent.py
- permission

## God Nodes (most connected - your core abstractions)
1. `bash` - 40 edges
2. `AgentService` - 28 edges
3. `DatabaseAdapter` - 22 edges
4. `SQLiteAdapter` - 22 edges
5. `OpenAICompatibleProvider` - 22 edges
6. `DatabaseSettings` - 21 edges
7. `ProviderRegistry` - 21 edges
8. `DatabaseError` - 20 edges
9. `QueryResult` - 18 edges
10. `PostgresAdapter` - 16 edges

## Surprising Connections (you probably didn't know these)
- `Golden set de preguntas EPH` --conceptually_related_to--> `No comparabilidad estricta antes y después de 1T 2019`  [INFERRED]
  README.md → datos_indec/EPH_nota_metodologica_1_trim_2019.pdf
- `Diccionario de metadatos de columnas` --references--> `Ponderadores de ingresos PONDII PONDIIO PONDIH`  [INFERRED]
  README.md → datos_indec/EPH_registro_1T2026.pdf
- `Vistas legibles personas y hogares` --references--> `Códigos especiales y no respuesta`  [INFERRED]
  README.md → datos_indec/EPH_registro_1T2026.pdf
- `Vistas legibles personas y hogares` --references--> `Identificadores CODUSU NRO_HOGAR COMPONENTE`  [INFERRED]
  README.md → datos_indec/EPH_registro_1T2026.pdf
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

## Communities (22 total, 7 thin omitted)

### Community 0 - "Evaluación y reproducibilidad"
Cohesion: 0.09
Nodes (21): buscar_zip(), construir_base(), convertir_tipos(), extraer_tablas(), leer_txt(), main(), tipo_sql(), validar_periodo() (+13 more)

### Community 1 - "Capa semántica EPH"
Cohesion: 0.11
Nodes (12): get_adapter(), get_settings(), DatabaseBackend, DatabaseSettings, create_database_adapter(), test_accepts_cloudflare_d1_identifier(), test_accepts_postgresql_connection_string(), test_default_sqlite_path_is_relative_to_project() (+4 more)

### Community 2 - "opencode.json"
Cohesion: 0.22
Nodes (9): agent, build, plan, permission, instructions, edit, permission, $schema (+1 more)

### Community 3 - "Carga y CLI"
Cohesion: 0.12
Nodes (16): Natural Language Query Agent on EPH, Architecture of Natural Language Query Agent on EPH, Decision Log for Natural Language Query Agent on EPH, Data for Natural Language Query Agent on EPH, Deployment of Natural Language Query Agent on EPH, Future Improvements for Natural Language Query Agent on EPH, Implementer for Natural Language Query Agent on EPH, Integrations for Natural Language Query Agent on EPH (+8 more)

### Community 4 - "Diseño de registros EPH 1T 2026"
Cohesion: 0.07
Nodes (27): Ajuste por calibración demográfica, Panel de rotación 2-2-2, Ajuste por propensity score, Umbrales de calidad para publicar resultados, Relevamiento telefónico EPH 2T 2020, Coeficientes de ajuste 2016-2018, Revisión de cobertura geográfica EPH, Ajuste de proyecciones de población (+19 more)

### Community 5 - "pytest"
Cohesion: 0.05
Nodes (27): DatabaseError, QueryExecutionError, QueryTimeoutError, D1Adapter, PostgresAdapter, _authorizer(), SQLiteAdapter, SQLGuardError (+19 more)

### Community 6 - "semantic.py"
Cohesion: 0.10
Nodes (26): _check_column_values(), _check_dictionary_structure(), describe_table(), _from_json(), install_semantic_layer(), list_views(), load_dictionary(), main() (+18 more)

### Community 12 - "bash"
Cohesion: 0.05
Nodes (39): cat*, curl *, docker *, find*, git add*, git commit*, git diff*, git log* (+31 more)

### Community 14 - "api.py"
Cohesion: 0.07
Nodes (33): ask_agent(), describe_table(), execute_sql(), health(), list_providers(), schema(), select_provider(), test_provider() (+25 more)

### Community 15 - "agent.py"
Cohesion: 0.07
Nodes (30): AgentError, AgentService, _dedupe(), detect_period_conflict(), quality_warnings(), _to_payload(), AgentAnswer, AnswerValidationError (+22 more)

### Community 16 - "test_api.py"
Cohesion: 0.11
Nodes (6): client(), client(), test_hosted_rechaza_base_url_arbitraria(), test_hosted_solo_lista_perfiles_permitidos(), write_providers(), test_execute_sql_rechaza_consultas_peligrosas()

### Community 17 - "providers/__init__.py"
Cohesion: 0.09
Nodes (15): _json_arguments(), LLMProvider, Message, ModelInfo, ModelNotFound, ModelTurn, ProviderAuthError, ProviderError (+7 more)

### Community 18 - "test_providers.py"
Cohesion: 0.15
Nodes (18): get_registry(), _default_path(), models_handler(), provider(), test_complete_with_tools_parsea_argumentos(), test_error_de_conexion_es_seguro(), test_health_credencial_invalida(), test_health_modelo_inexistente() (+10 more)

### Community 19 - "test_api_agent.py"
Cohesion: 0.22
Nodes (8): AlwaysToolsProvider, client(), FakeProvider, patch_provider(), fake_create(), test_agent_ask_acota_periodo(), test_agent_ask_devuelve_salida_auditable(), test_agent_ask_falla_si_no_termina()

### Community 20 - "permission"
Cohesion: 0.20
Nodes (10): permission, external_directory, glob, grep, list, read, task, todowrite (+2 more)

## Knowledge Gaps
- **25 isolated node(s):** `eph-agente`, `Perfiles local dev y eval`, `Despliegue reproducible en contenedor`, `Panel de rotación 2-2-2`, `Coeficientes de ajuste 2016-2018` (+20 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 211 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DatabaseError` connect `pytest` to `api.py`, `agent.py`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Are the 19 inferred relationships involving `AgentService` (e.g. with `AgentAnswer` and `ResultPayload`) actually correct?**
  _`AgentService` has 19 INFERRED edges - model-reasoned connections that need verification._
- **What connects `eph-agente`, `Perfiles local dev y eval`, `Despliegue reproducible en contenedor` to the rest of the system?**
  _25 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Evaluación y reproducibilidad` be split into smaller, more focused modules?**
  _Cohesion score 0.09468599033816426 - nodes in this community are weakly interconnected._
- **Why does `AgentService` connect `agent.py` to `providers/__init__.py`, `pytest`, `api.py`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `DatabaseAdapter` (e.g. with `AgentService` and `create_database_adapter()`) actually correct?**
  _`DatabaseAdapter` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Should `Capa semántica EPH` be split into smaller, more focused modules?**
  _Cohesion score 0.10984848484848485 - nodes in this community are weakly interconnected._