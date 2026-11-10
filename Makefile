.PHONY: install test lint format app validar-catalogo

install:
	uv sync --all-groups

test:
	uv run pytest -q

lint:
	uv run ruff check .

format:
	uv run ruff format .

validar-catalogo:
	uv run python -m rutas.data.catalogo

app:
	@echo 'La app todavía no existe (Fase 7).' && exit 1