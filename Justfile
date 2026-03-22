check: format lint test

test:
  uv run python -m pytest

lint:
  uv run ruff check --fix autobahn tests

format:
  uv run ruff format autobahn tests

format-check:
  uv run ruff format --check autobahn tests
