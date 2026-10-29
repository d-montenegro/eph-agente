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
