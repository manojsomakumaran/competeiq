.PHONY: help install install-dev lint format test test-ut test-it-api test-it-ui datasets ui cli build docker clean

help:
	@echo "Available targets:"
	@echo "  install        - Install runtime deps"
	@echo "  install-dev    - Install dev + test deps + editable package"
	@echo "  lint           - Run ruff + black --check + mypy"
	@echo "  format         - Run ruff --fix + black"
	@echo "  test           - Run unit tests"
	@echo "  test-ut        - Run unit tests"
	@echo "  test-it-api    - Run API integration tests (requires API keys)"
	@echo "  test-it-ui     - Run UI E2E tests (local only)"
	@echo "  datasets       - Generate sample catalog datasets"
	@echo "  ui             - Launch Gradio UI"
	@echo "  cli            - Show CLI help"
	@echo "  build          - Build wheel + sdist"
	@echo "  docker         - Build Docker images"
	@echo "  clean          - Remove build artifacts"

install:
	pip install -r requirements/base.txt

install-dev:
	pip install -r requirements/dev.txt -r requirements/test.txt
	pip install -e .

lint:
	ruff check src tests
	black --check src tests
	mypy src

format:
	ruff check --fix src tests
	black src tests

test: test-ut

test-ut:
	pytest -m unit

test-it-api:
	pytest -m integration_api

test-it-ui:
	pytest -m integration_ui

datasets:
	python -m competeiq.cli datasets generate

ui:
	python -m competeiq.cli ui

cli:
	python -m competeiq.cli --help

build:
	python -m build

docker:
	docker build -t competeiq:latest -f deploy/Dockerfile .
	docker build -t competeiq-ui:latest -f deploy/Dockerfile.ui .

clean:
	rm -rf build dist *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
