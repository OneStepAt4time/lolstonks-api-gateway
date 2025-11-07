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
	uv pip install -e .

install-dev:
	uv pip install -e ".[dev,docs]"
	uv run pre-commit install

# Development
test:
	uv run pytest --cov=app --cov-report=html --cov-report=term -v

test-quick:
	uv run pytest -v

test-unit:
	uv run pytest tests/unit/ -v

test-integration:
	uv run pytest tests/integration/ -v

test-all:
	uv run pytest -v

lint:
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy app/ --ignore-missing-imports || true

format:
	uv run ruff check --fix .
	uv run ruff format .

# Documentation
docs:
	uv run python scripts/generate_api_docs.py
	uv run mkdocs build --strict

docs-serve:
	uv run python scripts/generate_api_docs.py
	uv run mkdocs serve

docs-deploy:
	uv run python scripts/generate_api_docs.py
	uv run mkdocs gh-deploy --force

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
	uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8080

run-prod:
	uv run uvicorn app.main:app --host 127.0.0.1 --port 8080

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

# Full CI pipeline locally (simula GitHub Actions)
ci:
	@echo "🚀 Running CI pipeline locally (equivalent to GitHub Actions)..."
	@echo ""
	@echo "1️⃣  Installing dependencies..."
	@$(MAKE) install-dev
	@echo ""
	@echo "2️⃣  Running linting checks..."
	@$(MAKE) lint
	@echo ""
	@echo "3️⃣  Running tests with coverage..."
	@$(MAKE) test
	@echo ""
	@echo "4️⃣  Building documentation..."
	@$(MAKE) docs
	@echo ""
	@echo "✅ CI pipeline completed successfully!"
	@echo ""
	@echo "💡 This is equivalent to what GitHub Actions will run on push/PR"

# Simpler CI for quick checks
ci-quick:
	@echo "⚡ Running quick CI checks..."
	@$(MAKE) lint
	@$(MAKE) test-quick
	@echo "✅ Quick checks passed!"
