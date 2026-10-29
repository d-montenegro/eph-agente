# Graph Report - Trabajo Final Diplomatura  (2026-10-29)

## Corpus Check
- 77 files · ~36,149 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 9 file(s) not represented in the graph (top: (none) 5, .example 1, .zip 1)

## Summary
- 776 nodes · 1687 edges · 33 communities (26 shown, 7 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 177 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `23032874`
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
- Agente de consultas en lenguaje natural sobre la EPH
- Evaluación
- scripts
- dev.sh

## God Nodes (most connected - your core abstractions)
1. `bash` - 40 edges
2. `AgentService` - 30 edges
3. `DatabaseSettings` - 23 edges
4. `SQLiteAdapter` - 23 edges
5. `ProviderRegistry` - 23 edges
6. `DatabaseAdapter` - 22 edges
7. `OpenAICompatibleProvider` - 22 edges
8. `DatabaseError` - 20 edges
9. `QueryResult` - 18 edges
10. `PostgresAdapter` - 16 edges

## Surprising Connections (you probably didn't know these)
- `La solución` --references--> `describir_tabla()`  [INFERRED]
  docs/proyecto.md → src/eph_agent/tools.py
- `La solución` --references--> `ejecutar_sql()`  [INFERRED]
  docs/proyecto.md → src/eph_agent/tools.py
- `Golden set de preguntas EPH` --conceptually_related_to--> `No comparabilidad estricta antes y después de 1T 2019`  [INFERRED]
  README.md → datos_indec/EPH_nota_metodologica_1_trim_2019.pdf
- `Diccionario de metadatos de columnas` --references--> `Ponderadores de ingresos PONDII PONDIIO PONDIH`  [INFERRED]
  README.md → datos_indec/EPH_registro_1T2026.pdf
- `Vistas legibles personas y hogares` --references--> `Códigos especiales y no respuesta`  [INFERRED]
  README.md → datos_indec/EPH_registro_1T2026.pdf

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Architecture of Natural Language Query Agent on EPH** — agente_de_consultas_en_lenguaje_natural_sobre_la_eph_architecture, agente_de_consultas_en_lenguaje_natural_sobre_la_eph, agente_de_consultas_en_lenguaje_natural_sobre_la_eph_tests [EXTRACTED 0.75]
- **Data for Natural Language Query Agent on EPH** — agente_de_consultas_en_lenguaje_natural_sobre_la_eph_data, agente_de_consultas_en_lenguaje_natural_sobre_la_eph, agente_de_consultas_en_lenguaje_natural_sobre_la_eph_tests [EXTRACTED 0.75]
- **Metrics for Natural Language Query Agent on EPH** — agente_de_consultas_en_lenguaje_natural_sobre_la_eph_metrics, agente_de_consultas_en_lenguaje_natural_sobre_la_eph, agente_de_consultas_en_lenguaje_natural_sobre_la_eph_tests [EXTRACTED 0.75]
- **Acceso semántico seguro a la EPH** — readme_readable_views, readme_metadata_dictionary, readme_describir_tabla, readme_ejecutar_sql, readme_safe_sql_execution [EXTRACTED 1.00]
- **Ponderación y calidad de estimaciones EPH** — datos_indec_eph_registro_1t2026_general_weight, datos_indec_eph_registro_1t2026_income_weights, datos_indec_eph_consideraciones_metodologicas_2t20_propensity_score, datos_indec_eph_consideraciones_metodologicas_2t20_calibration, datos_indec_eph_consideraciones_metodologicas_2t20_quality_thresholds [INFERRED 0.85]

## Communities (33 total, 7 thin omitted)

### Community 0 - "Evaluación y reproducibilidad"
Cohesion: 0.09
Nodes (21): buscar_zip(), construir_base(), convertir_tipos(), extraer_tablas(), leer_txt(), main(), tipo_sql(), validar_periodo() (+13 more)

### Community 1 - "Capa semántica EPH"
Cohesion: 0.09
Nodes (13): get_settings(), DatabaseBackend, DatabaseSettings, create_database_adapter(), main(), repo_root(), test_accepts_cloudflare_d1_identifier(), test_accepts_postgresql_connection_string() (+5 more)

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
Nodes (27): DatabaseError, QueryExecutionError, QueryResult, QueryTimeoutError, D1Adapter, PostgresAdapter, _authorizer(), SQLiteAdapter (+19 more)

### Community 6 - "semantic.py"
Cohesion: 0.10
Nodes (31): _check_column_values(), _check_dictionary_structure(), describe_table(), _from_json(), install_semantic_layer(), list_views(), load_dictionary(), main() (+23 more)

### Community 12 - "bash"
Cohesion: 0.05
Nodes (39): cat*, curl *, docker *, find*, git add*, git commit*, git diff*, git log* (+31 more)

### Community 14 - "api.py"
Cohesion: 0.06
Nodes (44): CI, Despliegue, Docker, Local, Render (demo gratuita), Secretos, Variables, Vercel (frontend separado, opcional) (+36 more)

### Community 15 - "agent.py"
Cohesion: 0.08
Nodes (28): AgentError, AgentService, _dedupe(), detect_period_conflict(), quality_warnings(), _to_payload(), AgentAnswer, _as_list() (+20 more)

### Community 16 - "test_api.py"
Cohesion: 0.07
Nodes (14): AlwaysToolsProvider, client(), FakeProvider, patch_provider(), fake_create(), test_agent_ask_acota_periodo(), test_agent_ask_devuelve_salida_auditable(), test_agent_ask_falla_si_no_termina() (+6 more)

### Community 17 - "providers/__init__.py"
Cohesion: 0.10
Nodes (15): _json_arguments(), LLMProvider, Message, ModelInfo, ModelNotFound, ModelTurn, ProviderAuthError, ProviderError (+7 more)

### Community 18 - "pytest"
Cohesion: 0.11
Nodes (24): AnswerValidationError, get_registry(), _default_path(), test_validacion_rechaza_datos_sin_sql(), test_validacion_rechaza_texto_vacio(), models_handler(), provider(), test_complete_with_tools_parsea_argumentos() (+16 more)

### Community 19 - "evaluation.py"
Cohesion: 0.08
Nodes (36): _as_dict(), compare_result(), compare_runs(), _current_commit(), EvaluationError, extract_scalar(), inspect_sql(), load_cases() (+28 more)

### Community 20 - "permission"
Cohesion: 0.20
Nodes (10): permission, external_directory, glob, grep, list, read, task, todowrite (+2 more)

### Community 22 - "package.json"
Cohesion: 0.11
Nodes (16): jsdom, @testing-library/jest-dom, @types/node, @types/react, @types/react-dom, typescript, vite, @vitejs/plugin-react (+8 more)

### Community 23 - "client.ts"
Cohesion: 0.19
Nodes (11): ApiError, ProviderHealth, ProviderProfile, ProvidersResponse, QueryResult, request(), LABELS, ProviderStatus() (+3 more)

### Community 24 - "AgentPage.tsx"
Cohesion: 0.19
Nodes (11): react, @testing-library/react, AgentAnswer, formatValue(), Props, ResultTable(), Value, SqlPanel() (+3 more)

### Community 25 - "ProjectPage.tsx"
Cohesion: 0.27
Nodes (6): api, escapeHtml(), renderInline(), renderMarkdown(), Mode, ProjectPage()

### Community 26 - "compilerOptions"
Cohesion: 0.15
Nodes (12): compilerOptions, isolatedModules, jsx, lib, module, moduleResolution, noEmit, skipLibCheck (+4 more)

### Community 27 - "App.tsx"
Cohesion: 0.27
Nodes (6): react-dom, App(), Route, routeFromHash(), ROUTES, container

### Community 28 - "devDependencies"
Cohesion: 0.18
Nodes (11): devDependencies, jsdom, @testing-library/jest-dom, @testing-library/react, @types/node, @types/react, @types/react-dom, typescript (+3 more)

### Community 29 - "Agente de consultas en lenguaje natural sobre la EPH"
Cohesion: 0.29
Nodes (6): Agente de consultas en lenguaje natural sobre la EPH, Arquitectura, El problema, Evaluación, Lo que devuelve cada respuesta, Ponderadores

### Community 30 - "Evaluación"
Cohesion: 0.33
Nodes (5): Archivos, Comandos, Estructura de un caso, Evaluación, Umbral de aprobación (definido antes de mirar los resultados finales)

### Community 31 - "scripts"
Cohesion: 0.33
Nodes (6): scripts, build, dev, preview, test, typecheck

### Community 32 - "dev.sh"
Cohesion: 0.73
Nodes (5): ensure_setup(), is_running(), dev.sh script, start_one(), stop_one()

## Knowledge Gaps
- **31 isolated node(s):** `eph-agente`, `@types/react`, `@types/react-dom`, `jsdom`, `typescript` (+26 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 301 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AgentService` connect `agent.py` to `Capa semántica EPH`, `pytest`, `api.py`, `providers/__init__.py`, `evaluation.py`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Are the 19 inferred relationships involving `AgentService` (e.g. with `AgentAnswer` and `ResultPayload`) actually correct?**
  _`AgentService` has 19 INFERRED edges - model-reasoned connections that need verification._
- **What connects `eph-agente`, `@types/react`, `@types/react-dom` to the rest of the system?**
  _31 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Evaluación y reproducibilidad` be split into smaller, more focused modules?**
  _Cohesion score 0.09468599033816426 - nodes in this community are weakly interconnected._
- **Why does `ProviderRegistry` connect `api.py` to `providers/__init__.py`, `pytest`, `evaluation.py`, `Capa semántica EPH`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `DatabaseSettings` (e.g. with `get_adapter()` and `get_settings()`) actually correct?**
  _`DatabaseSettings` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Should `Capa semántica EPH` be split into smaller, more focused modules?**
  _Cohesion score 0.0859465737514518 - nodes in this community are weakly interconnected._