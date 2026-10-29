# Guía para agentes

## Objetivo del proyecto

Construir un agente auditable que responda preguntas en lenguaje natural sobre la
EPH del INDEC. Cada respuesta debe incluir el resultado, el SQL ejecutado, los
supuestos y las advertencias metodológicas aplicables.

## Reglas de dominio

- El alcance inicial es exclusivamente el 1T 2026.
- Las tablas crudas del INDEC se conservan intactas.
- El agente consulta únicamente vistas semánticas y metadatos versionados.
- Toda estimación debe usar el ponderador y el universo documentados.
- No agregar una métrica curada sin un fallo reproducible del golden set que la
  justifique.
- El SQL debe ser una única consulta de lectura, con timeout y límite de filas.
- Nunca incluir claves, tokens o contraseñas en archivos versionados.

## Desarrollo

- Trabajar en ramas distintas de `main`.
- Mantener SQLite como backend local reproducible.
- Mantener PostgreSQL como backend remoto principal.
- Tratar Cloudflare D1 como adaptador opcional; no mezclar su API con la lógica
  del agente.
- No usar Firestore para los microdatos EPH: no conserva el contrato SQL
  auditable. Puede usarse en el futuro para datos auxiliares de la aplicación.
- Agregar pruebas para cada cambio de datos, seguridad SQL o configuración.
- Consultar `dev-plans/2026-10-29-eph-web-agent.md` antes de implementar una
  fase nueva.

## Comandos esperados

- `make test`: pruebas rápidas.
- `make db`: reconstruir la base SQLite local.
- `make check`: formato, lint y pruebas.

## Delegación

- Los agentes de exploración y revisión no deben modificar archivos.
- Las tareas delegadas deben ser acotadas, verificables y no deben hacer push.
- Las decisiones sobre metodología EPH, ponderadores, seguridad SQL y golden set
  requieren revisión humana o del agente principal.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

When the user types `/graphify`, use the installed graphify skill or instructions before doing anything else.

Rules:
- When graphify-out/graph.json exists, run `graphify query "<question>"` before your first grep, search or source-file read for a codebase question, and put this rule in every subagent prompt that explores code. Read raw files only for lines the graph or an earlier read already located. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- Dirty graphify-out/ files are expected after hooks or incremental updates; dirty graph files are not a reason to skip graphify. Only skip graphify if the task is about stale or incorrect graph output, or the user explicitly says not to use it.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
- A committed graphify-out/graph.json is rewritten whole on every build, so a large diff to it in a pull request is expected. Do not flag it as churn or suggest skipping the graph rebuild or its hooks.

### Regeneración local (sin API key)

Este proyecto usa Ollama para la extracción semántica; no hace falta configurar
Gemini, Claude ni OpenAI. ChatGPT/Codex y OpenCode ejecutan `graphify` localmente
sobre el mismo `graphify-out/graph.json`; no se delegan entre sí.

- Consultar el grafo (`graphify query`, `explain`, `path`) no requiere API key.
- Reconstruir solo código: `graphify update .`.
- Reconstruir con docs y PDF (requiere Ollama en `localhost:11434`):
  `OLLAMA_API_KEY=local graphify extract . --backend ollama --model qwen2.5:7b --token-budget 8000 --allow-partial`
- Regenerar el reporte: `graphify cluster-only .`.
