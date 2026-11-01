# Graph Report - Trabajo Final Diplomatura  (2026-10-31)

## Corpus Check
- 81 files · ~39,077 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 10 file(s) not represented in the graph (top: (none) 5, .example 1, .zip 1)

## Summary
- 829 nodes · 1811 edges · 41 communities (34 shown, 7 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 199 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d0ccc977`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Evaluación y reproducibilidad
- Capa semántica EPH
- opencode.json
- Carga y CLI
- Golden set de preguntas EPH
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
- pytest
- evaluation.py
- permission
- package.json
- client.ts
- AgentPage.tsx
- ProjectPage.tsx
- compilerOptions
- App.tsx
- devDependencies
- test_api_agent.py
- Evaluación
- scripts
- dev.sh
- Despliegue
- Demo rápida
- Archivos originales del INDEC
- Sesgo por cobertura y no respuesta
- Diseño de registros EPH 1T 2026
- Herramienta ejecutar_sql
- Agente de consultas en lenguaje natural sobre la EPH
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
- `Golden set de preguntas EPH` --conceptually_related_to--> `No comparabilidad estricta antes y después de 1T 2019`  [INFERRED]
  README.md → datos_indec/EPH_nota_metodologica_1_trim_2019.pdf
- `La solución` --references--> `describir_tabla()`  [INFERRED]
  docs/proyecto.md → src/eph_agent/tools.py
- `La solución` --references--> `ejecutar_sql()`  [INFERRED]
  docs/proyecto.md → src/eph_agent/tools.py
- `Agente de consultas en lenguaje natural sobre la EPH` --conceptually_related_to--> `Umbrales de calidad para publicar resultados`  [INFERRED]
  README.md → datos_indec/EPH_consideraciones_metodologicas_2t20.pdf
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

## Communities (41 total, 7 thin omitted)

### Community 0 - "Evaluación y reproducibilidad"
Cohesion: 0.09
Nodes (21): buscar_zip(), construir_base(), convertir_tipos(), extraer_tablas(), leer_txt(), main(), tipo_sql(), validar_periodo() (+13 more)

### Community 1 - "Capa semántica EPH"
Cohesion: 0.08
Nodes (12): get_settings(), DatabaseBackend, DatabaseSettings, repo_root(), ColabNotebookTest, test_accepts_cloudflare_d1_identifier(), test_accepts_postgresql_connection_string(), test_default_sqlite_path_is_relative_to_project() (+4 more)

### Community 2 - "opencode.json"
Cohesion: 0.22
Nodes (9): agent, build, plan, permission, instructions, edit, permission, $schema (+1 more)

### Community 3 - "Carga y CLI"
Cohesion: 0.12
Nodes (16): Natural Language Query Agent on EPH, Architecture of Natural Language Query Agent on EPH, Decision Log for Natural Language Query Agent on EPH, Data for Natural Language Query Agent on EPH, Deployment of Natural Language Query Agent on EPH, Future Improvements for Natural Language Query Agent on EPH, Implementer for Natural Language Query Agent on EPH, Integrations for Natural Language Query Agent on EPH (+8 more)

### Community 4 - "Golden set de preguntas EPH"
Cohesion: 0.22
Nodes (6): Códigos especiales y no respuesta, Identificadores CODUSU NRO_HOGAR COMPONENTE, Golden set de preguntas EPH, Perfiles local dev y eval, Vistas legibles personas y hogares, Despliegue reproducible en contenedor

### Community 5 - "pytest"
Cohesion: 0.05
Nodes (28): DatabaseError, QueryExecutionError, QueryResult, QueryTimeoutError, D1Adapter, create_database_adapter(), PostgresAdapter, _authorizer() (+20 more)

### Community 6 - "semantic.py"
Cohesion: 0.10
Nodes (31): _check_column_values(), _check_dictionary_structure(), describe_table(), _from_json(), install_semantic_layer(), list_views(), load_dictionary(), main() (+23 more)

### Community 12 - "bash"
Cohesion: 0.05
Nodes (39): cat*, curl *, docker *, find*, git add*, git commit*, git diff*, git log* (+31 more)

### Community 14 - "api.py"
Cohesion: 0.06
Nodes (39): La solución, add_custom_provider(), ask_agent(), describe_table(), execute_sql(), get_adapter(), health(), list_providers() (+31 more)

### Community 15 - "agent.py"
Cohesion: 0.08
Nodes (34): AgentError, AgentService, _dedupe(), detect_period_conflict(), quality_warnings(), _to_payload(), AgentAnswer, AnswerValidationError (+26 more)

### Community 16 - "test_api.py"
Cohesion: 0.09
Nodes (7): client(), client(), test_hosted_no_permite_perfiles_personalizados(), test_hosted_rechaza_base_url_arbitraria(), test_hosted_solo_lista_perfiles_permitidos(), write_providers(), test_execute_sql_rechaza_consultas_peligrosas()

### Community 17 - "providers/__init__.py"
Cohesion: 0.09
Nodes (16): _json_arguments(), LLMProvider, Message, ModelInfo, ModelNotFound, ModelTurn, ProviderAuthError, ProviderError (+8 more)

### Community 18 - "pytest"
Cohesion: 0.13
Nodes (21): get_registry(), _default_path(), fake_create(), models_handler(), provider(), test_error_de_conexion_es_seguro(), test_health_credencial_invalida(), test_health_modelo_inexistente() (+13 more)

### Community 19 - "evaluation.py"
Cohesion: 0.08
Nodes (37): _as_dict(), compare_result(), compare_runs(), _current_commit(), EvaluationError, extract_scalar(), inspect_sql(), load_cases() (+29 more)

### Community 20 - "permission"
Cohesion: 0.20
Nodes (10): permission, external_directory, glob, grep, list, read, task, todowrite (+2 more)

### Community 22 - "package.json"
Cohesion: 0.11
Nodes (17): jsdom, @testing-library/jest-dom, @testing-library/react, @types/node, @types/react, @types/react-dom, typescript, vite (+9 more)

### Community 23 - "client.ts"
Cohesion: 0.16
Nodes (12): ApiError, CustomProviderInput, ProviderHealth, ProviderProfile, ProvidersResponse, QueryResult, request(), LABELS (+4 more)

### Community 24 - "AgentPage.tsx"
Cohesion: 0.17
Nodes (13): AgentAnswer, formatValue(), Props, ResultTable(), Value, SqlPanel(), writeText, AgentPage() (+5 more)

### Community 25 - "ProjectPage.tsx"
Cohesion: 0.27
Nodes (6): api, escapeHtml(), renderInline(), renderMarkdown(), Mode, ProjectPage()

### Community 26 - "compilerOptions"
Cohesion: 0.15
Nodes (12): compilerOptions, isolatedModules, jsx, lib, module, moduleResolution, noEmit, skipLibCheck (+4 more)

### Community 27 - "App.tsx"
Cohesion: 0.25
Nodes (7): react, react-dom, App(), Route, routeFromHash(), ROUTES, container

### Community 28 - "devDependencies"
Cohesion: 0.18
Nodes (11): devDependencies, jsdom, @testing-library/jest-dom, @testing-library/react, @types/node, @types/react, @types/react-dom, typescript (+3 more)

### Community 29 - "test_api_agent.py"
Cohesion: 0.22
Nodes (11): AlwaysToolsProvider, client(), FakeProvider, patch_provider(), test_agent_ask_acota_periodo(), test_agent_ask_con_debug_devuelve_traza(), test_agent_ask_devuelve_salida_auditable(), test_agent_ask_devuelve_ultimo_resultado_si_no_cierra() (+3 more)

### Community 30 - "Evaluación"
Cohesion: 0.33
Nodes (5): Archivos, Comandos, Estructura de un caso, Evaluación, Umbral de aprobación (definido antes de mirar los resultados finales)

### Community 31 - "scripts"
Cohesion: 0.33
Nodes (6): scripts, build, dev, preview, test, typecheck

### Community 32 - "dev.sh"
Cohesion: 0.73
Nodes (5): ensure_setup(), is_running(), dev.sh script, start_one(), stop_one()

### Community 33 - "Despliegue"
Cohesion: 0.22
Nodes (9): CI, Demo rápida, Despliegue, Docker, Local, Render (demo gratuita), Secretos, Variables (+1 more)

### Community 34 - "Demo rápida"
Cohesion: 0.25
Nodes (6): Umbrales de calidad para publicar resultados, Demo rápida, Opción A: Docker (recomendada para mostrar), Opción B: sin Docker, Validar los datos sin modelo, Agente de consultas en lenguaje natural sobre la EPH

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
Cohesion: 0.60
Nodes (4): Herramienta describir_tabla, Herramienta ejecutar_sql, Integración MCP con asistentes LLM, Loop de agente con tool use

### Community 39 - "Agente de consultas en lenguaje natural sobre la EPH"
Cohesion: 0.29
Nodes (6): Agente de consultas en lenguaje natural sobre la EPH, Arquitectura, El problema, Evaluación, Lo que devuelve cada respuesta, Ponderadores

### Community 40 - "DailyRequestLimiter"
Cohesion: 0.22
Nodes (6): get_query_limiter(), DailyRequestLimiter, test_bloquea_al_superar_el_limite(), test_cero_desactiva_el_limite(), test_rechaza_configuracion_invalida(), test_reinicia_el_contador_al_dia_siguiente()

## Knowledge Gaps
- **31 isolated node(s):** `eph-agente`, `@types/react`, `@types/react-dom`, `jsdom`, `typescript` (+26 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 319 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Secretos` connect `Despliegue` to `api.py`?**
  _High betweenness centrality (0.082) - this node is a cross-community bridge._
- **Are the 22 inferred relationships involving `AgentService` (e.g. with `AgentAnswer` and `ResultPayload`) actually correct?**
  _`AgentService` has 22 INFERRED edges - model-reasoned connections that need verification._
- **What connects `eph-agente`, `@types/react`, `@types/react-dom` to the rest of the system?**
  _31 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Evaluación y reproducibilidad` be split into smaller, more focused modules?**
  _Cohesion score 0.09468599033816426 - nodes in this community are weakly interconnected._
- **Why does `Despliegue` connect `Despliegue` to `Demo rápida`?**
  _High betweenness centrality (0.081) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `ProviderRegistry` (e.g. with `ProviderError` and `OpenAICompatibleProvider`) actually correct?**
  _`ProviderRegistry` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Should `Capa semántica EPH` be split into smaller, more focused modules?**
  _Cohesion score 0.07549361207897794 - nodes in this community are weakly interconnected._