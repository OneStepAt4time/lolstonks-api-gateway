.PHONY: help install install-dev test lint format docs docs-serve clean build

# Default target
help:
	@echo "LOLStonks API Gateway - Available Commands:"
	@echo ""
	@echo "  install      Install production dependencies"
	@echo "  install-dev  Install development dependencies"
	@echo "  test         Run tests"
	@echo "  lint         Run linting"
	@echo "  format       Format code"
	@echo "  docs         Build documentation"
	@echo "  docs-serve   Serve documentation locally"
	@echo "  clean        Clean build artifacts"
	@echo "  build        Build for production"
	@echo ""
	@echo "Development workflow:"
	@echo "  make install-dev"
	@echo "  make format"
	@echo "  make lint"
	@echo "  make test"
	@echo "  make docs-serve"

# Installation
install:
	pip install -e .

install-dev:
	pip install -e ".[dev,docs]"
	pre-commit install

# Development
test:
	pytest --cov=app --cov-report=html --cov-report=term -v

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

test-all:
	pytest -v

lint:
	ruff check .
	ruff format --check .
	mypy app/ --ignore-missing-imports || true

format:
	ruff check --fix .
	ruff format .

# Documentation
docs:
	python scripts/generate_api_docs.py
	mkdocs build --strict

docs-serve:
	python scripts/generate_api_docs.py
	mkdocs serve

docs-deploy:
	python scripts/generate_api_docs.py
	mkdocs gh-deploy --force

docs-clean:
	rm -rf site/

# Quality assurance
qa: lint test docs

pre-commit: format lint test

# Build and clean
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	rm -rf site/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

# Development server
run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

# Docker
docker-build:
	docker build -t lolstonks-api-gateway .

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

docker-logs:
	docker-compose logs -f

# Database/Memory
redis-start:
	docker run -d --name lolstonks-redis -p 6379:6379 redis:7-alpine

redis-stop:
	docker stop lolstonks-redis || true
	docker rm lolstonks-redis || true

# API testing
api-test:
	curl -f http://localhost:8080/health || echo "Server not running"

api-docs-test:
	curl -f http://localhost:8080/docs || echo "Server not running"

# Release
version:
	@python -c "import app.main; print(app.main.__version__)"

tag:
	@git tag -a v$(shell make -s version) -m "Release v$(shell make -s version)"
	@echo "Tag created: v$(shell make -s version)"
	@echo "Run 'git push origin v$(shell make -s version)' to push the tag"

# Monitoring
monitor:
	watch -n 5 'curl -s http://localhost:8080/health | jq .'

logs:
	tail -f logs/app.log || echo "No log file found"

# Quick setup for new developers
setup: install-dev redis-start
	@echo "Setup complete!"
	@echo "Run 'make run' to start the development server"
	@echo "Run 'make docs-serve' to serve documentation"
	@echo "Run 'make test' to run tests"

# Full CI pipeline locally
ci: lint test docs
	@echo "CI pipeline completed successfully!"