PYTHON ?= python3

.PHONY: setup db test lint check api opencode-config

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

opencode-config:
	opencode debug config
