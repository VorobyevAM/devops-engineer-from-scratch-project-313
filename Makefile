run:
	uv run python main.py

test:
	uv run python -m pytest

lint:
	uv run ruff check .
