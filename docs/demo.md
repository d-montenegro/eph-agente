# Demo rápida

## Opción A: Docker (recomendada para mostrar)

Requisitos: Docker Desktop. Para usar un modelo local, Ollama corriendo en la
máquina anfitriona con un modelo que soporte tool calling.

```bash
make demo          # docker compose up --build
```

Abrir **http://localhost:8010**.

1. Ir a **Configuración**.
2. Probar el perfil `local` (Ollama en la máquina anfitriona) o agregar uno:
   - **Ollama local:** URL `http://host.docker.internal:11434/v1`, modelo
     `qwen3.5:latest` (recomendado) o `qwen2.5:7b` (más rápido, menos confiable).
   - **Proveedor cloud:** URL `https://.../v1`, modelo, y pegar la clave. La
     clave queda solo en memoria del servidor y no se muestra.
3. **Probar conexión** y después **Usar**.
4. Ir a **Agente**, escribir la pregunta y, si querés ver qué pasa, activar
   **Modo debugging**. La traza muestra cada turno, las herramientas llamadas,
   el SQL y los errores.

Para bajar la demo:

```bash
make demo-down
```

Notas:

- La imagen reconstruye `eph.sqlite` desde el ZIP versionado y la sirve en modo
  de solo lectura.
- `EPH_MODE=local` permite URLs arbitrarias para la demo. No usar ese modo en
  una demo pública.
- En Linux, `host.docker.internal` se resuelve con `extra_hosts: host-gateway`
  (ya está en `docker-compose.yml`). En macOS/Windows funciona por defecto.
- Si el puerto `8010` está ocupado, cambiarlo en `docker-compose.yml`.
- Los perfiles y claves agregados desde la web viven en memoria: al reiniciar el
  contenedor hay que volver a cargarlos.

## Opción B: sin Docker

```bash
make up       # API en 8010 y web en 5180, con Ollama local
make status
make down
```

Abrir **http://127.0.0.1:5180**.

## Validar los datos sin modelo

```bash
make eval-reference
```

Ejecuta el `sql_esperado` del golden set (19 casos con SQL) y no necesita API
key ni modelo.
