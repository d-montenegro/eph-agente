#!/usr/bin/env bash
# Levanta API + web en segundo plano con logs en tmp/.
# Uso: scripts/dev.sh [up|down|status]
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

API_PORT="${EPH_API_PORT:-8010}"
WEB_PORT="${EPH_WEB_PORT:-5180}"
API_TARGET="http://127.0.0.1:${API_PORT}"
mkdir -p tmp

is_running() {
  local pid_file="$1"
  [ -f "$pid_file" ] && kill -0 "$(cat "$pid_file")" 2>/dev/null
}

stop_one() {
  local name="$1"
  local pid_file="tmp/${name}.pid"
  if is_running "$pid_file"; then
    kill "$(cat "$pid_file")" 2>/dev/null || true
    echo "Detenido ${name}"
  fi
  rm -f "$pid_file"
}

start_one() {
  local name="$1"
  shift
  local pid_file="tmp/${name}.pid"
  if is_running "$pid_file"; then
    echo "${name} ya está corriendo (pid $(cat "$pid_file"))"
    return
  fi
  nohup "$@" > "tmp/${name}.log" 2>&1 &
  echo $! > "$pid_file"
  echo "Iniciado ${name} (pid $(cat "$pid_file"))"
}

ensure_setup() {
  if [ ! -d .venv ]; then
    echo "Creando entorno con uv..."
    uv sync --extra dev --extra postgres
  fi
  if [ ! -f eph.sqlite ]; then
    echo "Construyendo la base..."
    make db
  fi
  if [ ! -d web/node_modules ]; then
    echo "Instalando dependencias web..."
    npm --prefix web install
  fi
}

case "${1:-up}" in
  up)
    ensure_setup
    start_one api env \
      EPH_AUTH_ENABLED=1 \
      EPH_USERS_FILE=config/users.yml \
      EPH_PROVIDERS_FILE=config/providers.ollama.example.yml \
      PYTHONPATH=src \
      .venv/bin/python -m uvicorn eph_agent.api:app \
      --host 127.0.0.1 --port "$API_PORT"
    start_one web env \
      EPH_API_TARGET="$API_TARGET" \
      npm --prefix web run dev -- --host 127.0.0.1 --port "$WEB_PORT"
    echo
    echo "Web:  http://127.0.0.1:${WEB_PORT}"
    echo "API:  ${API_TARGET}/api/health"
    echo "Logs: tmp/api.log y tmp/web.log"
    ;;
  down)
    stop_one web
    stop_one api
    ;;
  status)
    if is_running tmp/api.pid; then
      echo "API:  corriendo (pid $(cat tmp/api.pid)) -> ${API_TARGET}/api/health"
    else
      echo "API:  detenida"
    fi
    if is_running tmp/web.pid; then
      echo "Web:  corriendo (pid $(cat tmp/web.pid)) -> http://127.0.0.1:${WEB_PORT}"
    else
      echo "Web:  detenida"
    fi
    ;;
  *)
    echo "Uso: $0 [up|down|status]" >&2
    exit 1
    ;;
esac
