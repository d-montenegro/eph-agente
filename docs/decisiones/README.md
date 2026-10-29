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
