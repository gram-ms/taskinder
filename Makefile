.PHONY: install dev lint run

install:
	@.venv/bin/pip install -e ".[dev]" -q

dev:
	@.venv/bin/textual run --dev src/taskinder/__main__.py

lint:
	@.venv/bin/ruff check src
	@.venv/bin/ruff format src

run:
	@.venv/bin/taskinder
