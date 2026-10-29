PYTHON ?= python3

.PHONY: setup db test lint check api eval web web-test web-build opencode-config

setup:
	uv sync --extra dev --extra postgres

db:
	$(PYTHON) src/eph_a_sqlite.py
	PYTHONPATH=src $(PYTHON) -m eph_agent.semantic --db eph.sqlite --validate

test:
	PYTHONPATH=src $(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m ruff format --check .

check: lint test

api:
	PYTHONPATH=src $(PYTHON) -m uvicorn eph_agent.api:app --reload --port 8000

eval:
	PYTHONPATH=src $(PYTHON) -m eph_agent.evaluation --golden eval/golden.yml --repetitions 3 --profile local

web:
	npm --prefix web run dev

web-test:
	npm --prefix web test

web-build:
	npm --prefix web run build

opencode-config:
	opencode debug config
