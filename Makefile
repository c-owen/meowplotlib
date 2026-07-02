.PHONY: check

check:
	ruff check src tests && ruff format --check src tests && mypy src && pytest -q
