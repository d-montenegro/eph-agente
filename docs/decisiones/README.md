# Bitácora de decisiones

Registro cronológico de los cambios que afectan el comportamiento del agente.
Cada entrada sigue el mismo formato: fallo observado, hipótesis, cambio aplicado
y efecto medido sobre el golden set.

La bitácora sirve para dos cosas:

- Explicar por qué existe cada pieza de la capa semántica, las métricas o el prompt.
- Revisar qué se puede quitar cuando cambie el modelo.

## Plantilla

```markdown
## AAAA-MM-DD · título corto

- **Fallo:** qué pregunta del golden set falló y cómo (valor, SQL, supuesto).
- **Hipótesis:** la causa concreta que se quiere corregir.
- **Cambio:** un solo cambio (descripción, vista, métrica, prompt o validación).
- **Efecto:** preguntas corregidas, regresiones y resultado de la corrida completa.
- **Estado:** queda / se revierte.
- **Commit:** hash o referencia de la corrida.
```

## Reglas

- Un cambio por entrada: si se tocan dos cosas a la vez no se puede atribuir el efecto.
- El efecto se mide con el golden set completo, no solo con la pregunta que falló.
- Si el cambio no mejora o genera regresiones, se revierte y se registra igual.
- Las decisiones sobre ponderadores, universo y definiciones EPH requieren revisión humana.

## Entradas

### 2026-10-29 · Capa semántica inicial (fase 1)

- **Fallo:** no hay fallo de golden set todavía; se construye la superficie de
  datos que usará el agente.
- **Hipótesis:** exponer etiquetas legibles y aplicar universo/NULL en la vista
  reduce errores de ponderador y de población antes de escribir el prompt.
- **Cambio:** vistas `personas` y `hogares` sobre las tablas crudas, más
  `semantic/columns.yml` como diccionario versionado.
- **Supuestos registrados:**
  - `P21` (ingreso de la ocupación principal) es NULL fuera de los ocupados y
    cuando vale -9 (no respuesta); un 0 dentro del universo se conserva.
  - `P47T` es NULL cuando la entrevista no se realizó (`ESTADO = 0`) o cuando
    vale -9; un 0 se conserva.
  - `ITF`, `IPCF` y `PONDIH` se dejan como están: 0 es un valor válido y un
    ponderador 0 excluye a los hogares sin respuesta de ingresos.
  - `CH06 = -1` y `CH06 = 99` se convierten en NULL; 98, 100 y 101 son edades
    válidas.
  - `CAT_OCUP` 0 (fuera de universo) y 9 (Ns/Nr) se convierten en NULL.
  - Cada columna de ingreso declara su ponderador propio (`PONDIIO`, `PONDII`,
    `PONDIH`), distinto del `PONDERA` general.
- **Efecto:** 37 columnas documentadas; `validate_dictionary` valida vistas,
  tipos, valores, períodos y conteos contra la base real del 1T 2026.
- **Estado:** queda, sujeto a revisión metodológica humana.
- **Commit:** ver historial de la rama `codex/eph-web-configurable`.

### 2026-10-29 · Línea base local con qwen2.5:7b (no concluyente)

- **Fallo:** con Ollama local (`qwen2.5:7b`) la pregunta por la tasa de
  desocupación total devolvió `0` con SQL sin ponderador:
  `SUM(CASE WHEN es_desocupado = 1 THEN 1 ELSE 0 END) / SUM(...)`, que además
  cae en división entera de SQLite.
- **Hipótesis:** el modelo no aplicó la regla de ponderación ni el casteo a real.
- **Cambio:** se reforzó el prompt con la fórmula ponderada explícita y la regla
  de `* 1.0`.
- **Efecto:** al repetir la misma pregunta, el modelo no ejecutó SQL ni devolvió
  una respuesta final dentro de 4 turnos. El cambio empeoró el smoke local.
- **Decisión:** se revierte el cambio. No se corre el golden completo porque el
  perfil `local` no es el de medición de calidad; la línea base formal queda
  pendiente de un perfil `dev` o `eval`.
- **Estado:** revertido.
- **Commit:** ver historial de la rama `codex/eph-web-configurable`.

### 2026-10-29 · Revisión metodológica: tasas, universos y ponderadores

- **Fallo:** `lab_003` y `lab_004` calculaban actividad y empleo sobre
  `estado_actividad IS NOT NULL`, que incluía a los menores de 10 años
  (`ESTADO = 4`). Daban 48,74% y 44,92% cuando sobre la población de 10 años y
  más son 56,05% y 51,66%. Además, el campo `weight` del diccionario usaba los
  nombres crudos (`PONDERA`, `PONDIIO`, `PONDII`, `PONDIH`), que no son columnas
  consultables de las vistas.
- **Hipótesis:** el denominador de las tasas estaba mal definido y los metadatos
  de ponderación no coincidían con la superficie que ve el agente.
- **Cambio:**
  - Vistas: `P47T` solo para `ESTADO` 1, 2 o 3; `grupo_edad` es NULL si `CH06`
    es NULL.
  - Golden set: nuevos valores y supuestos para `lab_003` y `lab_004`; se
    explicita que el promedio de `ing_003` es sobre personas, no sobre hogares.
  - Prompt: definiciones de desocupación, actividad y empleo, y nombres de las
    columnas de ponderación de las vistas.
  - Diccionario: `weight` apunta a `pondera`, `pondera_ingreso_ocupacion`,
    `pondera_ingreso_total` y `pondera_ingreso_familiar`; se documentan los
    universos de ingresos, los Ns/Nr de empleo/sector y el riesgo de sumar
    ingresos de hogar sobre personas.
  - `validate_dictionary` ejecuta 11 checks de universo, claves y ponderadores
    definidos en `columns.yml`.
- **Efecto:** el smoke de referencia da 13/13 con los valores corregidos; la capa
  semántica pasa 19 pruebas, incluidas las de `P47T`, `grupo_edad` y ponderadores.
- **Estado:** queda, sujeto a revisión humana final.
- **Commit:** ver historial de la rama `codex/eph-web-configurable`.

### 2026-10-29 · Endurecimiento de proveedores y adaptadores

- **Fallo:** la revisión de seguridad encontró cuatro riesgos: una `base_url` con
  usuario/clave se habría devuelto en `/api/providers`; un perfil `hosted` podía
  usar `http`; PostgreSQL no garantizaba `READ ONLY` en la primera transacción; y
  el authorizer de SQLite permitía `load_extension`.
- **Hipótesis:** los perfiles y los adaptadores no validaban esas condiciones.
- **Cambio:** se rechazan credenciales embebidas, se exige `https` para perfiles
  hosted, PostgreSQL usa `connection.read_only = True`, y SQLite deniega
  `load_extension`. Se agregaron pruebas de regresión.
- **Efecto:** 122 pruebas en verde; el golden de referencia sigue 13/13.
- **Estado:** queda.
- **Commit:** ver historial de la rama `codex/eph-web-configurable`.
