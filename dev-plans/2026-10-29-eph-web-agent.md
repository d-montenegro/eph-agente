# Plan técnico: Web y agente de consultas sobre la EPH

| | |
|---|---|
| **Especificación** | Documento “Agente de consultas en lenguaje natural sobre la EPH” + requisitos de la conversación |
| **Repositorio analizado** | `https://github.com/d-montenegro/eph-agente` (`main`, commit `335ab87`) |
| **Fecha** | 2026-10-29 |
| **Estado** | Borrador para revisión |

## Resumen

El proyecto ampliará el repositorio existente con una aplicación web que permita: explicar y presentar el trabajo, consultar la EPH mediante un agente auditable y configurar perfiles de modelos locales o remotos. El MVP conservará la idea central del trabajo: una capa semántica versionada, SQL estrictamente de solo lectura, respuestas con valor/tabla, SQL, supuestos y advertencias, y evaluación reproducible mediante un golden set.

La recomendación es un monorepo con **FastAPI** para el backend y **React + Vite + TypeScript** para la interfaz. El backend encapsulará el acceso a SQLite y a los proveedores LLM; la interfaz nunca ejecutará SQL ni guardará claves directamente.

## Alcance

### Incluido en el MVP

- Aplicación web responsive con tres secciones:
  - **Proyecto**: explicación editable, vista previa y modo presentación.
  - **Agente EPH**: pregunta, respuesta, tabla, SQL, supuestos y advertencias.
  - **Configuración**: perfiles LLM, modelo, URL base y prueba de conectividad.
- Perfiles `local`, `dev` y `eval` intercambiables por configuración.
- Compatibilidad inicial con APIs estilo OpenAI (`/v1/models` y `/v1/chat/completions`).
- Soporte explícito para LM Studio/Ollama compatibles y OmniRoute.
- Capa semántica inicial para condición de actividad, demografía e ingresos.
- Ejecución SQLite de solo lectura con límites, timeout y bloqueo de sentencias peligrosas.
- Golden set inicial y registro reproducible de evaluaciones.
- Ejecución local mediante un solo comando y despliegue gratuito de demostración.

### Fuera del MVP

- Series históricas o incorporación automática de otros trimestres.
- Edición multiusuario de la presentación.
- Persistencia de conversaciones de usuarios en producción.
- Autenticación completa y administración remota de secretos.
- MCP público del agente; se deja preparado como fase posterior.

## Decisiones de arquitectura

### 1. Topología

```text
React/Vite
  ├─ Proyecto / presentación (borrador en localStorage + importar/exportar Markdown)
  ├─ Agente EPH
  └─ Configuración de perfiles
          │ HTTPS / JSON
          ▼
FastAPI
  ├─ AgentService
  ├─ ProviderRegistry ──► LLM local / OmniRoute / proveedor cloud
  ├─ QueryTools
  └─ DatabaseAdapter
       ├─ SQLite read-only (local)
       ├─ PostgreSQL read-only (hosted)
       └─ Cloudflare D1 (experimental)
              └─ vistas + metadatos + tablas crudas
```

### 2. Modos de ejecución

| Modo | Interfaz y backend | Modelo | Uso |
|---|---|---|---|
| `local` | Ambos en la computadora | LM Studio, Ollama, llama.cpp u OmniRoute local | Desarrollo y defensa con la PC propia |
| `hosted-demo` | Aplicación pública | Perfil cloud preconfigurado en variables de entorno | Mostrar el trabajo desde cualquier dispositivo |
| `eval` | Local o CI | Uno o más candidatos fijados | Ejecutar el golden set y comparar |

Una aplicación desplegada no puede interpretar `localhost` como la computadora del visitante: allí `localhost` es el propio servidor. Por eso el perfil local funcionará cuando el backend también corra localmente. El demo público usará un endpoint remoto configurado en el servidor.

### 2.1 Backends de datos configurables

- `sqlite`: backend local predeterminado y reproducible.
- `postgresql`: backend remoto principal para Neon, Supabase u otro PostgreSQL administrado.
- `cloudflare_d1`: backend experimental con dialecto SQLite y adaptador HTTP/Worker.
- Firestore no almacenará los microdatos porque no preserva el contrato SQL auditable; puede reservarse para preferencias o historial de la aplicación.

La selección se realiza con `EPH_DATABASE_BACKEND` y `EPH_DATABASE_URL`. La lógica del agente consume un `DatabaseAdapter`, no un driver concreto. SQLite y PostgreSQL deberán pasar el mismo golden set.

### 3. Edición de la presentación

- Fuente canónica versionada: `docs/proyecto.md`.
- En el navegador: editor Markdown, vista previa y modo presentación.
- El borrador se guarda en `localStorage` y puede importarse/exportarse como `.md`.
- “Restaurar versión del repositorio” vuelve a `docs/proyecto.md`.
- En el MVP la edición no escribe en el servidor. Esto evita sumar autenticación, una base de edición y conflictos multiusuario.

### 4. Contrato de proveedor LLM

Todos los perfiles se traducen a un contrato interno:

```python
class LLMProvider(Protocol):
    async def health(self) -> ProviderHealth: ...
    async def list_models(self) -> list[ModelInfo]: ...
    async def complete_with_tools(
        self,
        messages: list[Message],
        tools: list[ToolDefinition],
        *,
        model: str,
        temperature: float,
    ) -> ModelTurn: ...
```

Configuración no secreta por perfil:

- `name`: `local`, `dev`, `eval` u otro nombre.
- `base_url`: raíz que termina en `/v1`.
- `model`: identificador exacto devuelto por `/v1/models`.
- `api_mode`: inicialmente `chat_completions`; `responses` puede agregarse después.
- `timeout_seconds`, `max_retries` y `enabled`.
- `api_key_env`: nombre de la variable de entorno, nunca el valor de la clave.

El chequeo de conectividad será una llamada server-side a `GET <base_url>/models`, con timeout corto, medición de latencia y mensajes diferenciados para DNS/conexión, autenticación y modelo ausente.

### 5. Seguridad SQL

- Abrir SQLite con URI `mode=ro` y `PRAGMA query_only = ON`.
- Instalar un `sqlite3.Connection.set_authorizer()` que deniegue DDL, DML, `ATTACH`, `DETACH` y PRAGMA mutables.
- Parsear con `sqlglot`; aceptar una única sentencia de consulta (`SELECT`/CTE que termina en `SELECT`).
- Consultar únicamente vistas permitidas; las tablas crudas no entran al prompt ni a la lista blanca del ejecutor.
- Aplicar `LIMIT` máximo aunque el modelo no lo incluya.
- Aplicar timeout mediante `set_progress_handler()` y cancelar consultas largas.
- Devolver como máximo un número configurable de filas y registrar el SQL realmente ejecutado.
- No confiar en regex como única defensa.

## Análisis del repositorio actual

### Lo que ya existe

- `README.md`: especificación conceptual completa, arquitectura, perfiles, evaluación, riesgos y fases.
- `datos_indec/EPH_usu_1_Trim_2026_txt.zip`: microdatos originales (24 MB descomprimidos).
- `datos_indec/EPH_registro_1T2026.pdf`: diseño de registros y códigos.
- `datos_indec/EPH_nota_metodologica_1_trim_2019.pdf` y `EPH_consideraciones_metodologicas_2t20.pdf`: advertencias metodológicas.
- `src/eph_a_sqlite.py`: pipeline reproducible de carga.
- `src/requirements.txt`: solo `pandas==3.1.0`.

### Pipeline verificado

`src/eph_a_sqlite.py` se ejecutó sin cambios sobre el ZIP versionado y generó una base de aproximadamente 21 MB:

- `hogar`: 15.447 filas, 98 columnas.
- `individual`: 43.739 filas, 234 columnas.

Funciones existentes que se preservan y cubren con pruebas:

- `buscar_zip()` localiza un único archivo ZIP válido.
- `leer_txt()` maneja UTF-8/Latin-1 y CSV con separador `;`.
- `convertir_tipos()` conserva identificadores y convierte columnas numéricas.
- `extraer_tablas()` identifica las bases individual y hogar.
- `validar_periodo()` restringe la carga al 1T 2026.
- `construir_base()` recrea tablas, índices y ejecuta la carga transaccional.
- `main()` expone el proceso por CLI.

### Lo que falta

- No existen todavía vistas semánticas, metadatos, profiling ni métricas curadas.
- No existe el agente, sus herramientas ni los adaptadores LLM.
- No hay API, web, pruebas automáticas, golden set, contenedor ni CI.
- La validación SQL descripta en el README todavía no está implementada.

## Migración y ventana de transición

N/A para el MVP: el corte es instantáneo y no hay dos fuentes superpuestas de métricas, facturación o ventanas móviles. La base se reconstruye desde el ZIP y las vistas/metadatos se crean en el mismo proceso. Los borradores de presentación viven en el navegador y se pueden descartar sin afectar la fuente canónica.

## Fase 0: Base reproducible y entorno de trabajo

**Objetivo:** convertir el repositorio actual en una base testeable para el desarrollo incremental.

### Archivos

| Archivo | Acción | Descripción |
|---|---|---|
| `pyproject.toml` | Crear | Dependencias, herramientas y paquete Python. |
| `src/eph_agent/__init__.py` | Crear | Paquete de aplicación. |
| `src/eph_agent/config.py` | Crear | Configuración validada de SQLite, PostgreSQL y D1. |
| `tests/test_eph_a_sqlite.py` | Crear | Pruebas del cargador existente. |
| `tests/test_config.py` | Crear | Validación de backends y URLs. |
| `Makefile` | Crear | Comandos `setup`, `db`, `api`, `web`, `test` y `eval`. |
| `.env.example` | Crear | Variables sin secretos. |
| `docs/decisiones/README.md` | Crear | Plantilla de bitácora fallo/hipótesis/cambio/efecto. |
| `opencode.json` | Crear | Configuración versionada del proyecto para OpenCode. |
| `.opencode/agents/*.md` | Crear | Agentes delegables de datos, implementación y seguridad SQL. |

### Funciones

- Mantener la interfaz CLI existente de `src/eph_a_sqlite.py`.
- Extraer solo helpers cuando sea necesario para probar; no reescribir el pipeline sin evidencia.

### Criterios de aceptación

- [x] Una instalación limpia puede generar `eph.sqlite` desde el ZIP versionado.
- [x] La reconstrucción produce exactamente dos tablas crudas y los índices esperados.
- [x] Los conteos 15.447/43.739 quedan fijados como prueba de integridad del 1T 2026.
- [x] El repositorio documenta Python soportado y un único comando de preparación.
- [x] OpenCode carga la configuración del proyecto y descubre los agentes especializados.
- [x] SQLite, PostgreSQL y D1 tienen configuraciones validadas sin exponer secretos.
- [ ] El proyecto se registra en el Hub del orquestador para delegaciones remotas; mientras tanto puede delegarse con el CLI local.

### Checks

- [x] Lint/format de Python.
- [x] Pruebas unitarias del cargador.

## Fase 1: Capa semántica y profiling

**Objetivo:** crear la única superficie de datos que podrán consultar el agente y el ejecutor SQL.

### Archivos

| Archivo | Acción | Descripción |
|---|---|---|
| `semantic/views.sql` | Crear | Vistas `personas` y `hogares`. |
| `semantic/columns.yml` | Crear | Diccionario de columnas versionado. |
| `semantic/schema.sql` | Crear | Tablas de metadatos. |
| `src/eph_agent/semantic.py` | Crear | Instalación y validación de la capa semántica. |
| `src/eph_agent/profile.py` | Crear | Valores, rangos, nulos y comparación con el diccionario. |
| `tests/test_semantic_layer.py` | Crear | Universos, códigos especiales, ponderadores y joins. |

### Funciones

- `install_semantic_layer(connection)` crea metadatos y vistas en una transacción.
- `validate_dictionary(connection, dictionary)` detecta columnas faltantes, valores no documentados y tipos incompatibles.
- `profile_view(connection, view_name)` genera estadísticas reproducibles.

### Primer subconjunto de variables

- Identificación: `CODUSU`, `NRO_HOGAR`, `COMPONENTE`, `AGLOMERADO`.
- Demografía: sexo, edad, parentesco y grupo etario.
- Actividad: `ESTADO`, ocupación/desocupación/inactividad y ponderador `PONDERA`.
- Ingresos: `P21`, `P47T`, `ITF`, `IPCF` y ponderadores específicos `PONDII`, `PONDIIO`, `PONDIH`.

### Criterios de aceptación

- [x] El agente no necesita conocer códigos `CHxx` para las preguntas cubiertas.
- [x] Valores especiales y fuera de universo se convierten a `NULL` según documentación.
- [x] Personas y hogares se unen únicamente con identificadores documentados.
- [x] Cada columna expuesta declara descripción, tipo, valores, universo, significado de `NULL`, ponderador y sinónimos.
- [x] El profiling falla de forma explícita si datos y diccionario divergen.

### Checks

- [x] Pruebas de datos y regresión SQL.
- [ ] Revisión metodológica manual contra `EPH_registro_1T2026.pdf` (pendiente de aprobación humana).

## Fase 2: Backend, contratos y ejecución SQL segura

**Objetivo:** exponer herramientas determinísticas antes de conectar un modelo.

### Archivos

| Archivo | Acción | Descripción |
|---|---|---|
| `src/eph_agent/config.py` | Crear | Configuración tipada y modos local/hosted. |
| `src/eph_agent/database/base.py` | Crear | Protocolo común de base de datos. |
| `src/eph_agent/database/sqlite.py` | Crear | Conexión SQLite read-only y authorizer. |
| `src/eph_agent/database/postgres.py` | Crear | Pool PostgreSQL y transacciones read-only. |
| `src/eph_agent/database/d1.py` | Crear opcional | Adaptador HTTP experimental para Cloudflare D1. |
| `src/eph_agent/sql_guard.py` | Crear | Parseo, lista blanca, límite y timeout. |
| `src/eph_agent/tools.py` | Crear | `describir_tabla` y `ejecutar_sql`. |
| `src/eph_agent/schemas.py` | Crear | Modelos Pydantic de entrada/salida. |
| `src/eph_agent/api.py` | Crear | FastAPI y endpoints base. |
| `tests/test_sql_guard.py` | Crear | Matriz de consultas permitidas y rechazadas. |

### Endpoints

- `GET /api/health`
- `GET /api/schema`
- `POST /api/tools/describe-table`
- `POST /api/tools/execute-sql`

### Funciones

- `create_database_adapter(settings)` selecciona un backend sin cambiar el agente.
- `SQLiteAdapter.connect()` abre con `mode=ro` y `query_only`.
- `PostgresAdapter.connect()` usa un rol de solo lectura y TLS.
- `validate_query(sql)` devuelve AST validado o error seguro.
- `execute_bounded_query(sql, max_rows, timeout_ms)` ejecuta con límites.
- `describir_tabla(nombre)` devuelve la ficha versionada.

### Criterios de aceptación

- [x] `SELECT` y CTEs de lectura sobre vistas permitidas funcionan.
- [x] Múltiples sentencias, DML, DDL, `ATTACH`, PRAGMA mutable y tablas crudas se rechazan.
- [x] Una consulta costosa se cancela al superar el timeout.
- [x] El API nunca devuelve una traza o ruta sensible al cliente.
- [ ] La respuesta conserva el SQL realmente ejecutado y el tamaño muestral no ponderado (SQL sí; tamaño muestral queda para el loop del agente).
- [ ] SQLite y PostgreSQL producen resultados equivalentes para el mismo fixture (PostgreSQL implementado, falta una instancia para la prueba cruzada).
- [x] D1 no se marca como soportado hasta pasar las mismas pruebas de contrato.

### Checks

- [ ] Revisión de seguridad (pendiente de revisión independiente).
- [x] Pruebas unitarias y de integración.

## Fase 3: Perfiles LLM y diagnóstico de conectividad

**Objetivo:** cambiar de modelo o proveedor sin modificar el agente.

### Archivos

| Archivo | Acción | Descripción |
|---|---|---|
| `config/providers.example.yml` | Crear | Perfiles sin secretos. |
| `src/eph_agent/providers/base.py` | Crear | Protocolos y modelos comunes. |
| `src/eph_agent/providers/openai_compatible.py` | Crear | Implementación `/v1/models` y tool calling. |
| `src/eph_agent/providers/registry.py` | Crear | Selección y validación de perfiles. |
| `tests/test_providers.py` | Crear | Mocks de éxito, auth, timeout y modelo faltante. |

### Endpoints

- `GET /api/providers`: devuelve perfiles y configuración no secreta.
- `POST /api/providers/test`: comprueba URL, autenticación, latencia, modelos y tool calling.
- `POST /api/providers/select`: cambia el perfil de la sesión solo en modo local; en hosted usa lista permitida.

### Criterios de aceptación

- [x] LM Studio/Ollama compatible puede configurarse con una URL local.
- [ ] OmniRoute funciona con base URL terminada en `/v1` y modelo de `/v1/models` (configurado, falta prueba contra el servidor real).
- [ ] La UI distingue “servidor inaccesible”, “credencial inválida” y “modelo inexistente” (la API ya devuelve los estados; la UI llega en la fase 5).
- [x] Ningún endpoint devuelve el valor de una API key.
- [x] El modo hosted impide configurar destinos arbitrarios para evitar SSRF.
- [x] Cambiar de proveedor no modifica `AgentService` ni las herramientas.

### Checks

- [ ] Revisión de seguridad de secretos y SSRF (pendiente de revisión independiente).
- [x] Pruebas de contrato con un servidor compatible simulado.

## Fase 4: Loop del agente y salida auditable

**Objetivo:** implementar el agente mínimo evaluable con reintentos acotados.

### Archivos

| Archivo | Acción | Descripción |
|---|---|---|
| `src/eph_agent/agent.py` | Crear | Loop pregunta → tools → respuesta. |
| `src/eph_agent/prompts/system.md` | Crear | Prompt versionado. |
| `src/eph_agent/prompts/schema_index.py` | Crear | Índice compacto generado desde metadatos. |
| `src/eph_agent/answer.py` | Crear | Validación de la salida estructurada. |
| `tests/test_agent.py` | Crear | Tools, reintentos, ambigüedad y fallos. |

### Contrato de respuesta

```json
{
  "result": {"kind": "scalar|table", "value": null, "columns": [], "rows": []},
  "sql": "SELECT ...",
  "assumptions": ["..."],
  "warnings": ["..."],
  "answer": "...",
  "profile": "local",
  "model": "...",
  "sample_size": 0
}
```

### Funciones

- `AgentService.ask(question, profile)` coordina como máximo N turnos.
- `build_schema_index(metadata)` genera contexto compacto y determinístico.
- `validate_agent_answer(payload)` exige resultado, SQL, supuestos y texto.
- `quality_warnings(result, metadata)` agrega advertencias basadas en tamaño muestral y reglas documentadas.

### Criterios de aceptación

- [x] Cada respuesta exitosa incluye resultado, SQL, supuestos y texto.
- [x] Preguntas sobre otro período se rechazan o aclaran indicando 1T 2026.
- [x] Si el SQL falla, el modelo recibe un error sanitizado y puede corregirlo dentro del límite.
- [x] Al agotarse los turnos se devuelve un error útil, no una respuesta inventada.
- [x] La respuesta identifica perfil y modelo para reproducibilidad.

### Checks

- [x] Pruebas unitarias y de integración.
- [ ] Revisión de seguridad y de costos/latencia (pendiente).

## Fase 5: Web de proyecto, agente y configuración

**Objetivo:** entregar la experiencia de demostración y presentación.

### Archivos

| Archivo | Acción | Descripción |
|---|---|---|
| `web/package.json` | Crear | Dependencias y scripts. |
| `web/src/app.tsx` | Crear | Shell, navegación y manejo de errores. |
| `web/src/pages/ProjectPage.tsx` | Crear | Editor, preview y presentación. |
| `web/src/pages/AgentPage.tsx` | Crear | Consulta y respuesta auditable. |
| `web/src/pages/SettingsPage.tsx` | Crear | Perfiles y diagnóstico. |
| `web/src/api/client.ts` | Crear | Cliente tipado. |
| `web/src/components/SqlPanel.tsx` | Crear | SQL copiable y visible. |
| `web/src/components/ResultTable.tsx` | Crear | Tablas y valores. |
| `web/src/components/ProviderStatus.tsx` | Crear | Estado y latencia. |
| `docs/proyecto.md` | Crear | Narrativa canónica del trabajo. |
| `web/src/**/*.test.tsx` | Crear | Pruebas de componentes. |

### Criterios de aceptación

- [ ] Las tres secciones son navegables por URL y por pestañas.
- [ ] Proyecto permite editar, previsualizar, presentar, exportar, importar y restaurar.
- [ ] Agente muestra por separado respuesta, resultado, SQL, supuestos y advertencias.
- [ ] Configuración prueba la conexión antes de permitir seleccionar un perfil.
- [ ] La web funciona en pantalla de notebook y proyector sin texto cortado.
- [ ] Accesibilidad básica: teclado, foco visible, etiquetas y contraste.
- [ ] No se almacenan API keys en `localStorage`.

### Checks

- [ ] Lint, pruebas de componentes y smoke test de las tres rutas.
- [ ] Revisión UX para la defensa oral.

## Fase 6: Golden set y evaluación reproducible

**Objetivo:** medir calidad antes de decidir el modelo y antes de desplegar.

### Archivos

| Archivo | Acción | Descripción |
|---|---|---|
| `eval/golden.yml` | Crear | Casos visibles. |
| `eval/reserve.yml` | Crear | Reserva no usada durante la iteración. |
| `src/eph_agent/evaluation.py` | Crear | Runner, normalización y tolerancias. |
| `eval/runs/.gitkeep` | Crear | Carpeta de resultados versionables seleccionados. |
| `tests/test_evaluation.py` | Crear | Comparación de escala, tablas y SQL. |

### Funciones

- `run_case(case, profile, repetitions)` ejecuta y registra cada intento.
- `compare_result(actual, expected, tolerance)` normaliza porcentaje/fracción y tablas.
- `inspect_sql(sql, rules)` verifica vista, ponderador y universo.
- `compare_runs(previous, current)` identifica correcciones, ruido y regresiones.

### Criterios de aceptación

- [ ] Golden set inicial de condición de actividad, demografía e ingresos.
- [ ] Incluye trampas: conteo sin ponderar, período inexistente, aglomerado inválido y universo incorrecto.
- [ ] Cada corrida guarda commit, fecha, perfil, modelo, resultado, SQL y latencia.
- [ ] Se ejecutan tres repeticiones para mediciones formales.
- [ ] Un umbral de aprobación queda documentado antes de mirar los resultados finales.

### Checks

- [ ] Pruebas del evaluador.
- [ ] Corrida completa local y comparación entre al menos dos perfiles.

## Fase 7: Empaquetado y despliegue gratuito

**Objetivo:** ofrecer una demo pública sin cambiar la arquitectura local.

### Estrategia recomendada

1. **Primera opción: un único servicio Render Free** con Docker/FastAPI sirviendo también el build estático de React y PostgreSQL gratuito en Neon o Supabase.
   - Ventaja: un solo origen, sin CORS, proceso Python normal y SQLite de solo lectura incluido en la imagen.
   - Limitación: el servicio gratuito se duerme tras inactividad y el primer acceso puede tardar alrededor de un minuto.
   - SQLite puede seguir empaquetado para una demo cerrada, pero PostgreSQL evita depender del filesystem efímero.
2. **Opción de presentación: frontend en Vercel Hobby + backend en Render**.
   - Ventaja: frontend con arranque rápido, previews y buen flujo de despliegue.
   - Costo: dos servicios, CORS y configuración adicional.
3. **Vercel full-stack** se deja como experimento, no como camino principal.
   - Vercel soporta Python/FastAPI y archivos de lectura empaquetados, pero oficialmente no considera SQLite una base persistente compatible con su modelo serverless.
   - El backend no puede acceder al LLM que corre en `localhost` de la computadora del usuario.

### Archivos

| Archivo | Acción | Descripción |
|---|---|---|
| `Dockerfile` | Crear | Build web + runtime Python. |
| `render.yaml` | Crear | Servicio, build, start y health check. |
| `vercel.json` | Crear opcional | Deploy estático del frontend. |
| `.github/workflows/ci.yml` | Crear | Lint, tests, base y golden smoke. |
| `docs/deployment.md` | Crear | Local, Render, Vercel y variables. |

### Criterios de aceptación

- [ ] `docker build` reconstruye la base desde el ZIP y empaqueta una copia read-only.
- [ ] `/api/health` verifica proceso, base y perfil sin exponer secretos.
- [ ] El contenedor arranca localmente sin depender de rutas de la máquina del autor.
- [ ] El demo hosted usa solo perfiles remotos permitidos.
- [ ] CI bloquea el despliegue ante fallos de tests o regresión del smoke set.
- [ ] La respuesta pública siempre informa que los datos cubren 1T 2026.

### Checks

- [ ] Build de contenedor.
- [ ] Revisión de seguridad de imagen y secretos.
- [ ] Smoke test contra la URL desplegada.

## Fase 8: Validación final y defensa

**Objetivo:** demostrar que el producto, la metodología y la presentación cuentan la misma historia.

### Criterios finales

- [ ] La base se reconstruye de forma reproducible desde los originales del INDEC.
- [ ] Las variables expuestas tienen metadatos y universo documentados.
- [ ] El SQL es auditable y no puede modificar ni escapar de la base permitida.
- [ ] La misma pregunta puede correrse con perfiles distintos sin cambiar código.
- [ ] El perfil local se valida contra un LLM realmente ejecutado en la computadora.
- [ ] El perfil hosted funciona con secretos server-side.
- [ ] La web ofrece las tres secciones acordadas y modo presentación.
- [ ] El golden set mide resultados, SQL y estructura de salida.
- [ ] La bitácora explica al menos una mejora guiada por un fallo medido.
- [ ] La demo pública y el plan de contingencia local están probados antes de la defensa.

### Checks

- [ ] Lint y formato de todos los archivos modificados.
- [ ] Pruebas backend y frontend.
- [ ] Revisión de seguridad.
- [ ] Revisión de rendimiento y latencia.
- [ ] Golden set completo y conjunto de reserva.
- [ ] Ensayo de defensa sin internet usando el perfil local.

## Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Resultado plausible pero incorrecto | Capa semántica, ponderadores explícitos, SQL visible y golden set. |
| Modelo local sin tool calling confiable | Health check de capacidades y perfil `dev` para calidad. |
| Sobrediseñar para compensar un modelo chico | Cambios solo cuando un fallo reproducible lo justifica. |
| SQL malicioso o accidental | Parser, authorizer SQLite, solo lectura, lista blanca, timeout y límites. |
| Configuración arbitraria en producción | Allowlist server-side; URLs libres solo en modo local. |
| Filtración de claves | Variables de entorno; nunca devolver ni persistir claves en el navegador. |
| Demo gratuita dormida o sin red | Ensayo local completo y mensaje de warming-up en la interfaz. |
| Borrador de presentación perdido | Exportar/importar Markdown y restaurar fuente versionada. |
| Dependencia de un proveedor | Contrato `LLMProvider` y API OpenAI-compatible. |

## Delegación con OpenCode

El servidor OpenCode/OmniRoute está sano, pero el proyecto `eph-agente` todavía no está registrado en su Hub; por eso la primera delegación de revisión no pudo iniciarse. Después de la Fase 0, delegar en OpenCode estas tareas acotadas y verificables:

- Matriz inicial de pruebas del cargador.
- Scaffolding mecánico de modelos Pydantic y cliente TypeScript desde OpenAPI.
- Casos negativos del guard SQL.
- Pruebas de contrato del proveedor OpenAI-compatible.
- Componentes presentacionales sin lógica de dominio.
- Dockerfile/render.yaml y documentación de comandos.

Mantener en la sesión principal las decisiones metodológicas, el diccionario EPH, la seguridad SQL, los criterios del golden set y la revisión final de cada entrega.

## Orden de ejecución propuesto

1. Fases 0 y 1: base confiable y capa semántica.
2. Fases 2 y 3: herramientas seguras y perfiles LLM.
3. Fase 4: agente mínimo evaluable.
4. Fase 6: golden set inicial antes de pulir la interfaz.
5. Fase 5: web de demostración y presentación.
6. Fases 7 y 8: despliegue, validación y defensa.

La web no debe adelantarse a la capa semántica y al evaluador: una interfaz pulida no compensa números incorrectos. Sí conviene crear un shell visual mínimo temprano para validar navegación, pero el desarrollo principal debe seguir guiado por resultados medidos.

## Referencias técnicas verificadas

- Vercel MCP oficial: `https://vercel.com/docs/agent-resources/vercel-mcp`.
- Python en Vercel: `https://vercel.com/docs/functions/runtimes/python`.
- Filesystem de Vercel Functions: `https://vercel.com/docs/functions/runtimes`.
- SQLite en Vercel: `https://vercel.com/kb/guide/is-sqlite-supported-in-vercel`.
- Render Free: `https://render.com/docs/free`.
- FastAPI en Render: `https://render.com/docs/deploy-fastapi`.
- OmniRoute OpenAI compatibility: `https://github.com/cheaper-inference/OmniRoute/wiki/Openai-Compatibility`.

