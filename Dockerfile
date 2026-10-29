# syntax=docker/dockerfile:1

FROM node:22-alpine AS web
WORKDIR /app/web
COPY web/package.json web/package-lock.json ./
RUN npm ci
COPY web/ ./
RUN npm run build

FROM python:3.13-slim AS runtime
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    EPH_ROOT=/app \
    EPH_DATABASE_BACKEND=sqlite \
    EPH_DATABASE_URL=sqlite:///eph.sqlite \
    EPH_MODE=hosted
WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY semantic ./semantic
COPY config ./config
COPY docs ./docs
COPY eval ./eval
COPY datos_indec/EPH_usu_1_Trim_2026_txt.zip ./datos_indec/
COPY --from=web /app/web/dist ./web/dist

RUN pip install --no-cache-dir . \
    && python src/eph_a_sqlite.py \
    && PYTHONPATH=src python -m eph_agent.semantic --db eph.sqlite --validate

EXPOSE 8000
CMD ["uvicorn", "eph_agent.api:app", "--host", "0.0.0.0", "--port", "8000"]
