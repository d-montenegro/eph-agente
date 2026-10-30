# Despliegue

## Demo rápida

Para mostrar el trabajo en un solo comando, ver [`docs/demo.md`](demo.md):

```bash
make demo       # Docker Compose en http://localhost:8010
make demo-down
```

La demo permite cambiar la URL y el modelo desde la web, usar Ollama local o un
proveedor cloud, y activar el modo debugging para ver la traza del agente.

## Local

```bash
uv sync --extra dev --extra postgres
make db                 # reconstruye eph.sqlite + capa semántica
make eval-reference     # valida los valores del golden set sin LLM
make api                # FastAPI en http://127.0.0.1:8000
make api-ollama         # FastAPI con el perfil local de Ollama
make web                # Vite en http://127.0.0.1:5173 (proxy /api)
```

Para levantarlo todo en segundo plano, con API en 8010 y web en 5180:

```bash
make up       # crea el entorno/base si falta y arranca API + web
make status
make down
```

Los puertos se pueden cambiar con `EPH_API_PORT` y `EPH_WEB_PORT`; Vite usa
`EPH_API_TARGET` para el proxy. Los logs quedan en `tmp/api.log` y `tmp/web.log`.

`make api-ollama` y `make up` usan `config/providers.ollama.example.yml`
(`http://127.0.0.1:11434/v1`, modelo `qwen2.5:7b`). Requiere Ollama corriendo y
un modelo con tool calling. La calidad de un modelo 7B no es concluyente: para
medir calidad usá un perfil `dev` o `eval`.

Para servir la web compilada desde el propio FastAPI:

```bash
make web-build
make api           # sirve web/dist en / y la API en /api
```

El perfil local se configura en `config/providers.example.yml` (o en un
`config/providers.yml` propio). Las claves se resuelven desde variables de
entorno; el YAML solo guarda el nombre de la variable.

## Docker

```bash
docker build -t eph-agente .
docker run --rm -p 8000:8000 \
  -e EPH_MODE=local \
  -e EPH_LLM_API_KEY=... \
  eph-agente
```

La imagen:

1. compila la web (`web/dist`) en una etapa Node;
2. instala el paquete Python;
3. reconstruye `eph.sqlite` desde el ZIP versionado;
4. instala y valida la capa semántica;
5. sirve API y web con un único proceso.

La base viaja dentro de la imagen en modo de solo lectura. Si se actualizan los
microdatos, se reconstruye la imagen.

## Render (demo gratuita)

`render.yaml` define un servicio Docker con health check en `/api/health`.

1. Crear el servicio desde el repo (Blueprint o Web Service Docker).
2. Cargar los secretos en el panel:
   - `EPH_LLM_API_KEY`
   - `EPH_ALLOWED_LLM_HOSTS` (host del proveedor, sin `https://`)
3. Ajustar `config/providers.hosted.example.yml` (o crear
   `config/providers.yml`) con la `base_url` y el `model` reales.
4. Verificar `GET /api/health`: debe devolver `status: ok`, backend, dialecto,
   vistas y perfil.

El plan gratuito duerme el servicio tras inactividad; el primer acceso puede
tardar alrededor de un minuto.

## Vercel (frontend separado, opcional)

El frontend soporta `VITE_API_BASE` para apuntar a un backend remoto:

```bash
cd web
VITE_API_BASE=https://eph-agente.onrender.com npm run build
```

Sin esa variable usa rutas relativas (`/api/...`), que es lo recomendado cuando
FastAPI sirve también el build estático.

## Variables

| Variable | Uso |
|---|---|
| `EPH_DATABASE_BACKEND` | `sqlite`, `postgresql` o `cloudflare_d1` (experimental). |
| `EPH_DATABASE_URL` | URL del backend; nunca se devuelve al cliente. |
| `EPH_MODE` | `local` o `hosted`. En hosted se aplica la lista blanca de hosts. |
| `EPH_PROVIDERS_FILE` | Ruta al YAML de perfiles. |
| `EPH_ALLOWED_LLM_HOSTS` | Hosts remotos permitidos en hosted, separados por coma. |
| `EPH_LLM_API_KEY` | Clave del proveedor; solo como secreto. |
| `VITE_API_BASE` | URL del backend cuando la web se despliega aparte. |

## Secretos

- Las claves viven en variables de entorno o en el gestor de secretos de la
  plataforma, nunca en el YAML ni en el frontend.
- `GET /api/providers` devuelve `api_key_env` y `has_api_key`, jamás el valor.
- En modo hosted no se aceptan `base_url` arbitrarias: solo perfiles con
  `hosted: true` y host en la lista blanca.

## CI

`.github/workflows/ci.yml` bloquea el merge si fallan:

- lint/formato y pruebas del backend;
- reconstrucción de la base y validación del diccionario;
- smoke determinístico del golden set (ejecuta el `sql_esperado` de referencia);
- pruebas y build del frontend.

La evaluación con un modelo real (`make eval`) se corre aparte, cuando hay un
proveedor configurado y una clave disponible.
