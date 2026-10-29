# Agente de consultas en lenguaje natural sobre la EPH

Trabajo final de la diplomatura. Un agente que responde preguntas sobre el
mercado laboral y los ingresos de la Argentina usando los microdatos de la
Encuesta Permanente de Hogares (EPH) del INDEC, con respuestas auditables.

## El problema

Los microdatos de la EPH usan nombres y códigos ilegibles: el sexo está en la
columna `CH04` con 1 y 2, la condición de actividad en `ESTADO` con 0 a 4, y los
ingresos tienen códigos especiales (-9 es "no respondió"). Un modelo de lenguaje
que consulte esas tablas sin contexto produce números plausibles y equivocados:
olvida el ponderador, promedia fuera del universo o cuenta casos en lugar de
personas.

## La solución

Tres capas, cada una auditable:

1. **Capa semántica.** Sobre las tablas crudas —intactas, tal como las publica el
   INDEC— se construyen las vistas `personas` y `hogares`, con nombres legibles
   (`sexo = 'Mujer'`), valores especiales convertidos en `NULL` y el universo
   aplicado en los datos: el ingreso de la ocupación principal no existe fuera de
   los ocupados.
2. **Metadatos versionados.** Un diccionario (`semantic/columns.yml`) describe
   cada columna: qué mide, qué valores toma, qué significa un `NULL`, a quién
   aplica y con qué ponderador se estima. El agente consulta ese diccionario, no
   los códigos del INDEC.
3. **Agente con herramientas.** Un único loop pregunta → herramientas →
   respuesta. Dos herramientas determinísticas: `describir_tabla` y
   `ejecutar_sql`. El SQL pasa por un guard que solo permite una consulta
   `SELECT` sobre las vistas permitidas, con límite de filas y timeout.

## Lo que devuelve cada respuesta

- El valor o la tabla resultante.
- El SQL realmente ejecutado.
- Los supuestos: qué ponderador usó, qué universo, qué período.
- Advertencias: muestras chicas, resultados truncados, períodos fuera de
  alcance.

Los datos cubren **1T 2026**. Cualquier pregunta sobre otro período se rechaza
con esa aclaración en lugar de inventar una cifra.

## Ponderadores

La EPH no cuenta personas: las expande. Toda estimación usa el ponderador que
corresponde: `PONDERA` para demografía y tasas laborales, `PONDIIO` para el
ingreso de la ocupación principal, `PONDII` para el ingreso total individual y
`PONDIH` para los ingresos del hogar. El diccionario declara el ponderador de
cada columna y la evaluación verifica que el SQL lo use.

## Evaluación

Un golden set de 22 preguntas visibles más 4 de reserva, con valores esperados,
tolerancias y reglas sobre el SQL (vista, ponderador, universo). Los casos de
ingresos se validaron contra el informe del INDEC
(*Evolución de la distribución del ingreso, 1T 2026*): ingreso per cápita
familiar $728.008, ocupados con ingresos $1.104.227, asalariados $1.136.558 y
perceptores $1.153.457. Incluye trampas: pedir la población total (donde
`COUNT(*)` sin ponderar da 43.739 en lugar de 30 millones), períodos
inexistentes, aglomerados que no están en la muestra y universos incorrectos.
Cada corrida se repite tres veces y se guarda con commit, perfil, modelo, SQL y
latencia.

## Arquitectura

- **Backend** FastAPI con el agente, los adaptadores de base (SQLite local,
  PostgreSQL remoto) y los perfiles de modelos compatibles con OpenAI
  (LM Studio, Ollama, OmniRoute o cualquier proveedor en la nube).
- **Frontend** React + Vite con tres secciones: esta presentación, el agente y
  la configuración de perfiles.
- **Evaluación** reproducible con `make eval`.

Todo lo que define el comportamiento —vistas, diccionario, prompts y golden
set— está versionado en el repositorio.
