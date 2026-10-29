# Evaluación

El golden set mide el resultado **por ejecución**: compara el valor devuelto por
el agente con el esperado y verifica reglas sobre el SQL (vistas, ponderador y
universo). No evalúa la redacción salvo que el caso sea de rechazo o sin datos.

## Archivos

- `golden.yml`: casos visibles, usados durante la iteración.
- `reserve.yml`: conjunto de reserva, no se usa para ajustar prompts.
- `runs/`: corridas guardadas en JSON (commit, fecha, perfil, modelo, resultado,
  SQL y latencia).

## Umbral de aprobación (definido antes de mirar los resultados finales)

- Cada caso se corre **3 veces** en las mediciones formales.
- Un caso aprueba solo si **3/3** intentos coinciden con el valor esperado
  (dentro de la tolerancia) y no violan las reglas de SQL.
- Un modelo candidato queda habilitado si:
  - alcanza **≥ 90%** de casos aprobados en `golden.yml`;
  - acierta **100%** de los casos de `categoria: trampas`;
  - alcanza **≥ 80%** en `reserve.yml`.
- Una regresión es un caso que pasaba 3/3 y pasa a 0/3. Una caída a 2/3 se
  registra como caso frágil, no como regresión.

Los valores esperados se calcularon sobre los microdatos del 1T 2026 y quedan
pendientes de validación contra el informe técnico del INDEC. Cuando exista el
valor publicado, se reemplaza el esperado y se conserva la fuente.

## Comandos

```bash
make eval                      # perfil local, 3 repeticiones
PYTHONPATH=src python -m eph_agent.evaluation \
  --golden eval/golden.yml --repetitions 3 --profile dev
PYTHONPATH=src python -m eph_agent.evaluation \
  --golden eval/reserve.yml --repetitions 3 --profile eval
```

## Estructura de un caso

```yaml
- id: lab_001
  pregunta: "¿Cuál fue la tasa de desocupación total en el 1T 2026?"
  tipo: numero            # numero | tabla | rechazo | sin_datos
  valor_esperado: 0.078309
  unidad: fraccion        # fraccion | porcentaje | absoluta
  tolerancia: 0.0005
  categoria: tasas_laborales
  dificultad: baja
  fuente: "Cálculo de referencia sobre microdatos; pendiente INDEC"
  sql_esperado: "SELECT ..."
  reglas_sql:
    vistas: [personas]
    columnas: [pondera]
    texto: [Desocupado, Ocupado]
  supuestos: ["..."]
```

Para tablas, usar `columns` y `rows`. Para `rechazo` y `sin_datos` no se exige
`valor_esperado`.
