.PHONY: install test lint format app

install:
	uv sync --all-groups

test:
	uv run pytest -q

lint:
	uv run ruff check .

format:
	uv run ruff format .

app:
	uv run streamlit run app/streamlit_app.py