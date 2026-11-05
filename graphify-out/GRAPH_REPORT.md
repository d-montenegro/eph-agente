# Graph Report - Trabajo Final Diplomatura  (2026-11-05)

## Corpus Check
- 87 files · ~43,400 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 5, .zip 2, .example 1)

## Summary
- 904 nodes · 1998 edges · 42 communities (34 shown, 8 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 213 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9e2236e7`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Evaluación y reproducibilidad
- Capa semántica EPH
- opencode.json
- Carga y CLI
- Golden set de preguntas EPH
- DatabaseError
- semantic.py
- Validación del período
- eph-agente
- bash
- Dependencia pandas 3.1.0
- api.py
- AgentService
- test_api.py
- providers/__init__.py
- pytest
- evaluation.py
- permission
- package.json
- agent.py
- client.ts
- validate_query
- compilerOptions
- PostgresAdapter
- DatabaseAdapter
- test_api_agent.py
- Evaluación
- schema_index.py
- dev.sh
- Despliegue
- Demo rápida
- Archivos originales del INDEC
- Sesgo por cobertura y no respuesta
- Diseño de registros EPH 1T 2026
- Herramienta ejecutar_sql
- describir_tabla
- auth.py
- DailyRequestLimiter

## God Nodes (most connected - your core abstractions)
1. `bash` - 40 edges
2. `AgentService` - 34 edges
3. `ProviderRegistry` - 26 edges
4. `DatabaseSettings` - 23 edges
5. `SQLiteAdapter` - 23 edges
6. `DatabaseAdapter` - 22 edges
7. `OpenAICompatibleProvider` - 22 edges
8. `DatabaseError` - 20 edges
9. `QueryResult` - 19 edges
10. `PostgresAdapter` - 16 edges

## Surprising Connections (you probably didn't know these)
- `La solución` --references--> `ejecutar_sql()`  [INFERRED]
  docs/proyecto.md → src/eph_agent/tools.py
- `Golden set de preguntas EPH` --conceptually_related_to--> `No comparabilidad estricta antes y después de 1T 2019`  [INFERRED]
  README.md → datos_indec/EPH_nota_metodologica_1_trim_2019.pdf
- `La solución` --references--> `describir_tabla()`  [INFERRED]
  docs/proyecto.md → src/eph_agent/tools.py
- `Herramientas` --references--> `ejecutar_sql()`  [INFERRED]
  src/eph_agent/prompts/system.md → src/eph_agent/tools.py
- `Diccionario de metadatos de columnas` --references--> `Ponderadores de ingresos PONDII PONDIIO PONDIH`  [INFERRED]
  README.md → datos_indec/EPH_registro_1T2026.pdf

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Architecture of Natural Language Query Agent on EPH** — agente_de_consultas_en_lenguaje_natural_sobre_la_eph_architecture, agente_de_consultas_en_lenguaje_natural_sobre_la_eph, agente_de_consultas_en_lenguaje_natural_sobre_la_eph_tests [EXTRACTED 0.75]
- **Data for Natural Language Query Agent on EPH** — agente_de_consultas_en_lenguaje_natural_sobre_la_eph_data, agente_de_consultas_en_lenguaje_natural_sobre_la_eph, agente_de_consultas_en_lenguaje_natural_sobre_la_eph_tests [EXTRACTED 0.75]
- **Metrics for Natural Language Query Agent on EPH** — agente_de_consultas_en_lenguaje_natural_sobre_la_eph_metrics, agente_de_consultas_en_lenguaje_natural_sobre_la_eph, agente_de_consultas_en_lenguaje_natural_sobre_la_eph_tests [EXTRACTED 0.75]
- **Acceso semántico seguro a la EPH** — readme_readable_views, readme_metadata_dictionary, readme_describir_tabla, readme_ejecutar_sql, readme_safe_sql_execution [EXTRACTED 1.00]
- **Ponderación y calidad de estimaciones EPH** — datos_indec_eph_registro_1t2026_general_weight, datos_indec_eph_registro_1t2026_income_weights, datos_indec_eph_consideraciones_metodologicas_2t20_propensity_score, datos_indec_eph_consideraciones_metodologicas_2t20_calibration, datos_indec_eph_consideraciones_metodologicas_2t20_quality_thresholds [INFERRED 0.85]

## Communities (42 total, 8 thin omitted)

### Community 0 - "Evaluación y reproducibilidad"
Cohesion: 0.13
Nodes (17): buscar_zip(), construir_base(), convertir_tipos(), extraer_tablas(), leer_txt(), main(), tipo_sql(), validar_periodo() (+9 more)

### Community 1 - "Capa semántica EPH"
Cohesion: 0.08
Nodes (13): get_adapter(), get_settings(), DatabaseBackend, DatabaseSettings, create_database_adapter(), ColabNotebookTest, test_accepts_cloudflare_d1_identifier(), test_accepts_postgresql_connection_string() (+5 more)

### Community 2 - "opencode.json"
Cohesion: 0.22
Nodes (9): agent, build, plan, permission, instructions, edit, permission, $schema (+1 more)

### Community 3 - "Carga y CLI"
Cohesion: 0.12
Nodes (16): Natural Language Query Agent on EPH, Architecture of Natural Language Query Agent on EPH, Decision Log for Natural Language Query Agent on EPH, Data for Natural Language Query Agent on EPH, Deployment of Natural Language Query Agent on EPH, Future Improvements for Natural Language Query Agent on EPH, Implementer for Natural Language Query Agent on EPH, Integrations for Natural Language Query Agent on EPH (+8 more)

### Community 4 - "Golden set de preguntas EPH"
Cohesion: 0.25
Nodes (5): Umbrales de calidad para publicar resultados, Agente de consultas en lenguaje natural sobre la EPH, Golden set de preguntas EPH, Perfiles local dev y eval, Despliegue reproducible en contenedor

### Community 5 - "DatabaseError"
Cohesion: 0.18
Nodes (4): DatabaseError, QueryExecutionError, QueryTimeoutError, D1Adapter

### Community 6 - "semantic.py"
Cohesion: 0.08
Nodes (36): main(), profile_view(), _check_column_values(), _check_dictionary_structure(), describe_table(), _from_json(), install_semantic_layer(), list_views() (+28 more)

### Community 12 - "bash"
Cohesion: 0.05
Nodes (39): cat*, curl *, docker *, find*, git add*, git commit*, git diff*, git log* (+31 more)

### Community 14 - "api.py"
Cohesion: 0.08
Nodes (36): add_custom_provider(), ask_agent(), cancel_agent(), describe_table(), execute_sql(), health(), list_providers(), login() (+28 more)

### Community 15 - "AgentService"
Cohesion: 0.17
Nodes (18): AgentError, AgentService, detect_period_conflict(), FakeProvider, final(), sql_call(), test_agota_los_turnos_sin_inventar(), test_debug_incluye_la_traza_del_loop() (+10 more)

### Community 16 - "test_api.py"
Cohesion: 0.09
Nodes (7): client(), client(), test_hosted_no_permite_perfiles_personalizados(), test_hosted_rechaza_base_url_arbitraria(), test_hosted_solo_lista_perfiles_permitidos(), write_providers(), test_execute_sql_rechaza_consultas_peligrosas()

### Community 17 - "providers/__init__.py"
Cohesion: 0.09
Nodes (15): _json_arguments(), LLMProvider, Message, ModelInfo, ModelNotFound, ModelTurn, ProviderAuthError, ProviderError (+7 more)

### Community 18 - "pytest"
Cohesion: 0.07
Nodes (34): get_registry(), _authorizer(), SQLiteAdapter, _default_path(), adapter(), adapter(), test_acota_las_filas_devueltas(), test_base_inexistente_falla_con_mensaje_seguro() (+26 more)

### Community 19 - "evaluation.py"
Cohesion: 0.08
Nodes (37): _as_dict(), compare_result(), compare_runs(), _current_commit(), EvaluationError, extract_scalar(), inspect_sql(), load_cases() (+29 more)

### Community 20 - "permission"
Cohesion: 0.20
Nodes (10): permission, external_directory, glob, grep, list, read, task, todowrite (+2 more)

### Community 22 - "package.json"
Cohesion: 0.06
Nodes (31): jsdom, @types/node, @types/react, @types/react-dom, typescript, vite, @vitejs/plugin-react, dependencies (+23 more)

### Community 23 - "agent.py"
Cohesion: 0.14
Nodes (13): _dedupe(), quality_warnings(), _to_payload(), AgentAnswer, AnswerValidationError, _as_list(), normalize_structured(), parse_structured_answer() (+5 more)

### Community 24 - "client.ts"
Cohesion: 0.05
Nodes (52): react, react-dom, @testing-library/jest-dom, @testing-library/react, vitest, AgentAnswer, api, ApiError (+44 more)

### Community 25 - "validate_query"
Cohesion: 0.22
Nodes (8): SQLGuardError, validate_query(), test_acepta_cte_y_join_entre_vistas(), test_acepta_lectura_sobre_vistas(), test_acepta_select_sin_tablas(), test_aplica_el_limite_configurado(), test_rechaza_consultas_peligrosas(), test_rechaza_dml_escondido_en_cte()

### Community 26 - "compilerOptions"
Cohesion: 0.15
Nodes (12): compilerOptions, isolatedModules, jsx, lib, module, moduleResolution, noEmit, skipLibCheck (+4 more)

### Community 28 - "DatabaseAdapter"
Cohesion: 0.23
Nodes (3): DatabaseAdapter, QueryResult, ejecutar_sql()

### Community 29 - "test_api_agent.py"
Cohesion: 0.15
Nodes (13): AlwaysToolsProvider, client(), FakeProvider, patch_provider(), fake_create(), test_agent_ask_acota_periodo(), test_agent_ask_con_debug_devuelve_traza(), test_agent_ask_devuelve_salida_auditable() (+5 more)

### Community 30 - "Evaluación"
Cohesion: 0.33
Nodes (5): Archivos, Comandos, Estructura de un caso, Evaluación, Umbral de aprobación (definido antes de mirar los resultados finales)

### Community 31 - "schema_index.py"
Cohesion: 0.48
Nodes (3): build_schema_index(), _describe_column(), _render_value()

### Community 32 - "dev.sh"
Cohesion: 0.73
Nodes (5): ensure_setup(), is_running(), dev.sh script, start_one(), stop_one()

### Community 33 - "Despliegue"
Cohesion: 0.20
Nodes (10): Autenticación, CI, Demo rápida, Despliegue, Docker, Local, Render (demo gratuita), Secretos (+2 more)

### Community 34 - "Demo rápida"
Cohesion: 0.29
Nodes (5): Demo rápida, Opción A: Docker (recomendada para mostrar), Opción B: sin Docker, Usuarios y seguridad, Validar los datos sin modelo

### Community 35 - "Archivos originales del INDEC"
Cohesion: 0.33
Nodes (4): Coeficientes de ajuste 2016-2018, Revisión de cobertura geográfica EPH, Ajuste de proyecciones de población, Archivos originales del INDEC

### Community 36 - "Sesgo por cobertura y no respuesta"
Cohesion: 0.40
Nodes (5): Ajuste por calibración demográfica, Panel de rotación 2-2-2, Ajuste por propensity score, Relevamiento telefónico EPH 2T 2020, Ponderador general PONDERA

### Community 37 - "Diseño de registros EPH 1T 2026"
Cohesion: 0.40
Nodes (6): Condición de actividad ESTADO, Variables demográficas CH03-CH16, Campos de ingresos P21 P47T ITF IPCF, Ponderadores de ingresos PONDII PONDIIO PONDIH, Diseño de registros EPH 1T 2026, Diccionario de metadatos de columnas

### Community 38 - "Herramienta ejecutar_sql"
Cohesion: 0.32
Nodes (7): Códigos especiales y no respuesta, Identificadores CODUSU NRO_HOGAR COMPONENTE, Herramienta describir_tabla, Herramienta ejecutar_sql, Integración MCP con asistentes LLM, Vistas legibles personas y hogares, Loop de agente con tool use

### Community 39 - "describir_tabla"
Cohesion: 0.11
Nodes (13): Agente de consultas en lenguaje natural sobre la EPH, Arquitectura, El problema, Evaluación, La solución, Lo que devuelve cada respuesta, Ponderadores, Dialecto SQLite (+5 more)

### Community 40 - "auth.py"
Cohesion: 0.07
Nodes (20): main(), auth_guard(), AuthConfigError, _b64decode(), _b64encode(), blocked_ips(), hash_password(), LoginThrottle (+12 more)

### Community 44 - "DailyRequestLimiter"
Cohesion: 0.22
Nodes (6): get_query_limiter(), DailyRequestLimiter, test_bloquea_al_superar_el_limite(), test_cero_desactiva_el_limite(), test_rechaza_configuracion_invalida(), test_reinicia_el_contador_al_dia_siguiente()

## Knowledge Gaps
- **31 isolated node(s):** `eph-agente`, `@types/react`, `@types/react-dom`, `jsdom`, `typescript` (+26 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 339 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Secretos` connect `Despliegue` to `api.py`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **Are the 22 inferred relationships involving `AgentService` (e.g. with `AgentAnswer` and `ResultPayload`) actually correct?**
  _`AgentService` has 22 INFERRED edges - model-reasoned connections that need verification._
- **What connects `eph-agente`, `@types/react`, `@types/react-dom` to the rest of the system?**
  _31 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Evaluación y reproducibilidad` be split into smaller, more focused modules?**
  _Cohesion score 0.13015873015873017 - nodes in this community are weakly interconnected._
- **Why does `Despliegue` connect `Despliegue` to `Demo rápida`?**
  _High betweenness centrality (0.078) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `ProviderRegistry` (e.g. with `ProviderError` and `OpenAICompatibleProvider`) actually correct?**
  _`ProviderRegistry` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Should `Capa semántica EPH` be split into smaller, more focused modules?**
  _Cohesion score 0.08333333333333333 - nodes in this community are weakly interconnected._