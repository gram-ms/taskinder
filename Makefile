.PHONY: install lint

install:
	@.venv/bin/python -m pip install -e .

lint:
	@.venv/bin/ruff check src
	@.venv/bin/ruff format src
