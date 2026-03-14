.PHONY: help install install-dev clean test lint format type-check docs build docker-build docker-run docker-stop

help:
	@echo "Dual-RAG-Evaluator Development Commands"
	@echo "========================================"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install          Install dependencies"
	@echo "  make install-dev      Install with development tools"
	@echo "  make clean            Remove cache and build artifacts"
	@echo ""
	@echo "Development:"
	@echo "  make run              Run the GUI application"
	@echo "  make test             Run all tests"
	@echo "  make test-unit        Run unit tests only"
	@echo "  make test-integration Run integration tests only"
	@echo "  make test-coverage    Run tests with coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint             Run linting (flake8)"
	@echo "  make format           Format code with black and isort"
	@echo "  make type-check       Run type checking with mypy"
	@echo "  make check            Run all quality checks (lint + type + format check)"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs             Generate documentation with Sphinx"
	@echo "  make docs-serve       Serve documentation locally"
	@echo ""
	@echo "Distribution:"
	@echo "  make build            Build distribution packages"
	@echo "  make build-wheel      Build wheel distribution"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build     Build Docker image"
	@echo "  make docker-run       Run application in Docker"
	@echo "  make docker-stop      Stop Docker container"
	@echo "  make docker-shell     Open shell in Docker container"
	@echo ""

## Setup & Installation

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -e ".[dev,docs]"

## Cleanup

clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '*.egg-info' -exec rm -rf {} +
	find . -type d -name '.pytest_cache' -exec rm -rf {} +
	find . -type d -name '.mypy_cache' -exec rm -rf {} +
	find . -type d -name 'htmlcov' -exec rm -rf {} +
	find . -type d -name 'dist' -exec rm -rf {} +
	find . -type d -name 'build' -exec rm -rf {} +
	rm -f .coverage
	rm -f .coverage.*

## Running

run:
	python -m src.ui.main_window

## Testing

test:
	pytest tests/ -v --cov=src --cov-report=html

test-unit:
	pytest tests/unit/ -v -m unit

test-integration:
	pytest tests/integration/ -v -m integration

test-coverage:
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing
	@echo "Coverage report generated in htmlcov/index.html"

## Code Quality

lint:
	flake8 src/ tests/ --max-line-length=100 --statistics

format:
	black src/ tests/
	isort src/ tests/

format-check:
	black src/ tests/ --check
	isort src/ tests/ --check-only

type-check:
	mypy src/ --ignore-missing-imports

check: lint type-check format-check
	@echo "All checks passed!"

## Documentation

docs:
	cd docs && sphinx-build -b html . _build

docs-serve:
	python -m http.server --directory docs/_build 8000

## Distribution

build:
	python -m build

build-wheel:
	python -m pip install wheel
	python setup.py bdist_wheel

## Docker

docker-build:
	docker build -t dual-rag-evaluator:latest .

docker-run:
	docker run --rm -it \
		-v $(PWD)/data:/app/data \
		-v $(PWD)/results:/app/results \
		-e DISPLAY=$(DISPLAY) \
		-v /tmp/.X11-unix:/tmp/.X11-unix \
		dual-rag-evaluator:latest

docker-stop:
	docker stop dual-rag-evaluator || true
	docker rm dual-rag-evaluator || true

docker-shell:
	docker exec -it dual-rag-evaluator /bin/bash

docker-logs:
	docker logs -f dual-rag-evaluator

docker-compose-up:
	docker-compose up -d

docker-compose-down:
	docker-compose down

docker-compose-logs:
	docker-compose logs -f

## Development Environment

venv:
	python -m venv venv
	. venv/bin/activate && pip install --upgrade pip setuptools wheel

setup: venv install-dev
	@echo "Development environment ready!"
	@echo "Run: source venv/bin/activate (or venv\\Scripts\\activate on Windows)"
