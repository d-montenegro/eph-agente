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

Sin entradas todavía.
