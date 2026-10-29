PYTHON ?= python3

.PHONY: setup db test lint check opencode-config

setup:
	$(PYTHON) -m pip install -e '.[dev,postgres]'

db:
	$(PYTHON) src/eph_a_sqlite.py

test:
	PYTHONPATH=src $(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m ruff format --check .

check: lint test

opencode-config:
	opencode debug config
