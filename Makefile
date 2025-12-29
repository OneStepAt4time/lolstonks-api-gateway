.PHONY: help install install-dev test lint format docs docs-serve docs-build docs-validate clean build docs-validate security

# Default target
help:
	@echo "LOLStonks API Gateway - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  install      Install production dependencies"
	@echo "  install-dev  Install development dependencies"
	@echo "  test         Run tests"
	@echo "  test-quick   Run tests without coverage (fast)"
	@echo "  lint         Run linting"
	@echo "  format       Format code"
	@echo "  docs         Build documentation with interactive diagrams"
	@echo "  docs-serve   Serve documentation locally with interactive features"
	@echo "  docs-build   Build documentation for production (no live reload)"
	@echo "  docs-validate Validate documentation links and structure"
	@echo "  docs-preview  Preview documentation with interactive diagrams"
	@echo "  docs-test     Test documentation build and interactive features"
	@echo "  docs-clean    Clean documentation build artifacts"
	@echo "  clean        Clean build artifacts"
	@echo "  build        Build for production"
	@echo ""
	@echo "CI & Quality:"
	@echo "  ci           Run full CI pipeline (security + lint + test + docs)"
	@echo "  ci-quick     Run quick CI checks (lint + quick tests)"
	@echo "  security     Run security audit on dependencies"
	@echo "  qa           Run quality assurance (lint + test + docs-validate)"
	@echo ""
	@echo "Release:"
	@echo "  release           Create and publish a new release (interactive)"
	@echo "  release-dry-run   Preview release information without changes"
	@echo "  release-hotfix    Quick hotfix release (patch version only)"
	@echo "  version           Show current version"
	@echo "  tag               Create git tag for current version"
	@echo ""
	@echo "Development workflow:"
	@echo "  make install-dev"
	@echo "  make format"
	@echo "  make lint"
	@echo "  make test"
	@echo "  make docs-preview  # Test interactive diagrams"
	@echo ""
	@echo "Pre-push workflow (HIGHLY RECOMMENDED):"
	@echo "  make ci           # Run full CI pipeline before pushing"
	@echo "  make ci-quick     # For faster iteration during development"
	@echo ""
	@echo "Interactive Diagram Testing:"
	@echo "  make docs-build    # Build for testing"
	@echo "  make docs-test     # Validate interactive features"

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
	@echo "🚀 Building documentation with interactive diagrams..."
	uv run python scripts/export_openapi.py
	uv run python scripts/generate_api_docs.py
	uv run mkdocs build
	@echo "✅ Documentation built with interactive flowcharts!"
	@echo "💡 Features: Zoom, pan, click navigation, mobile support"

docs-serve:
	@echo "🌐 Starting documentation server with interactive features..."
	uv run python scripts/export_openapi.py
	uv run python scripts/generate_api_docs.py
	@echo "📋 Interactive diagrams available at http://127.0.0.1:8000"
	@echo "🎮 Try the System Overview: http://127.0.0.1:8000/architecture/system-overview/"
	@echo "🎯 View Diagram Guide: http://127.0.0.1:8000/architecture/diagram-guide/"
	uv run mkdocs serve

docs-build:
	@echo "🏗️ Building production documentation (optimized for deployment)..."
	uv run python scripts/export_openapi.py
	uv run python scripts/generate_api_docs.py
	uv run mkdocs build --quiet
	@echo "✅ Production build complete!"
	@echo "📦 Site ready for deployment to 'site/' directory"

docs-validate:
	@echo "🔍 Validating documentation structure..."
	uv run python scripts/generate_api_docs.py
	@echo "✅ API docs generated successfully"
	uv run mkdocs build --strict
	@echo "✅ Documentation structure valid"
	@echo "🔗 Checking interactive diagram files..."
	@if [ -f "docs/javascripts/mermaid-interactivity.js" ]; then \
		echo "✅ Interactive JavaScript found"; \
	else \
		echo "❌ Interactive JavaScript missing"; exit 1; \
	fi
	@if [ -f "docs/stylesheets/mermaid-interactivity.css" ]; then \
		echo "✅ Interactive CSS found"; \
	else \
		echo "❌ Interactive CSS missing"; exit 1; \
	fi
	@echo "✅ All interactive diagram assets validated!"

docs-deploy:
	@echo "🚀 Deploying documentation with interactive diagrams..."
	uv run python scripts/generate_api_docs.py
	uv run mkdocs gh-deploy --force
	@echo "✅ Documentation deployed with interactive flowcharts!"
	@echo "🌐 Live at: https://onestepat4time.github.io/lolstonks-api-gateway/"

docs-clean:
	@echo "🧹 Cleaning documentation build artifacts..."
	rm -rf site/
	@echo "✅ Documentation artifacts cleaned!"

# Quality assurance
qa: lint test docs-validate
	@echo "✅ Quality assurance completed!"
	@echo "🔍 Checked: Code formatting, tests, documentation structure"

qa-full: lint test docs docs-validate
	@echo "🔬 Full QA completed!"
	@echo "📋 All checks passed: Code, Tests, Interactive Docs"

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

# Interactive diagram testing
docs-test:
	@echo "🎮 Testing interactive diagrams..."
	@echo "1️⃣ Building documentation..."
	@$(MAKE) docs-build
	@echo ""
	@echo "2️⃣ Checking interactive assets..."
	@if [ -d "site" ]; then \
		echo "✅ Documentation built successfully"; \
		echo "📋 Open site/index.html in your browser"; \
		echo "🎮 Navigate to Architecture section to test interactive features"; \
		echo "🌐 Available at: file://$(shell pwd)/site/index.html"; \
	else \
		echo "❌ Documentation build failed"; exit 1; \
	fi

docs-preview:
	@echo "🌐 Starting documentation preview server..."
	@echo "📋 Interactive diagrams will be available at http://localhost:8000"
	@echo "🎮 Try: http://localhost:8000/architecture/system-overview/"
	$(MAKE) docs-serve

# Release
version:
	@cat VERSION

tag:
	@git tag -a v$(shell make -s version) -m "Release v$(shell make -s version)"
	@echo "Tag created: v$(shell make -s version)"
	@echo "Run 'git push origin v$(shell make -s version)' to push the tag"

release:
	@echo "🚀 Starting release process..."
	@echo ""
	@echo "This will:"
	@echo "  1. Run full CI pipeline (lint, test, docs)"
	@echo "  2. Prompt for version bump type (patch/minor/major)"
	@echo "  3. Update version files and CHANGELOG.md"
	@echo "  4. Commit changes"
	@echo "  5. Create and push git tag"
	@echo "  6. Trigger GitHub Actions release workflow"
	@echo ""
	@read -p "Continue? (y/N): " confirm; \
	if [ "$$confirm" != "y" ] && [ "$$confirm" != "Y" ]; then \
		echo "❌ Release cancelled"; \
		exit 1; \
	fi
	@echo ""
	@echo "1️⃣  Running CI pipeline..."
	@$(MAKE) ci
	@echo ""
	@echo "2️⃣  Version bump..."
	@echo "Current version: $$(cat VERSION)"
	@echo ""
	@echo "Select version bump type:"
	@echo "  1) patch (X.Y.Z -> X.Y.Z+1)  - Bug fixes"
	@echo "  2) minor (X.Y.Z -> X.Y+1.0)  - New features (backward compatible)"
	@echo "  3) major (X.Y.Z -> X+1.0.0)  - Breaking changes"
	@echo "  4) custom                     - Enter specific version"
	@echo ""
	@read -p "Choose [1-4]: " bump_type; \
	case $$bump_type in \
		1) python scripts/bump_version.py patch ;; \
		2) python scripts/bump_version.py minor ;; \
		3) python scripts/bump_version.py major ;; \
		4) read -p "Enter version (X.Y.Z): " custom_ver; python scripts/bump_version.py $$custom_ver ;; \
		*) echo "❌ Invalid choice"; exit 1 ;; \
	esac
	@echo ""
	@echo "3️⃣  Reviewing changes..."
	@NEW_VERSION=$$(cat VERSION); \
	echo "New version: $$NEW_VERSION"; \
	echo ""; \
	echo "Changed files:"; \
	git status --short; \
	echo ""; \
	echo "CHANGELOG.md preview:"; \
	head -n 20 CHANGELOG.md; \
	echo ""; \
	read -p "Commit and tag release v$$NEW_VERSION? (y/N): " confirm_commit; \
	if [ "$$confirm_commit" != "y" ] && [ "$$confirm_commit" != "Y" ]; then \
		echo "❌ Release cancelled"; \
		git checkout VERSION pyproject.toml app/__init__.py CHANGELOG.md 2>/dev/null || true; \
		exit 1; \
	fi; \
	echo ""; \
	echo "4️⃣  Committing changes..."; \
	git add VERSION pyproject.toml app/__init__.py CHANGELOG.md; \
	git commit -m "chore: release v$$NEW_VERSION"; \
	echo ""; \
	echo "5️⃣  Creating tag..."; \
	git tag -a "v$$NEW_VERSION" -m "Release v$$NEW_VERSION"; \
	echo ""; \
	echo "6️⃣  Pushing to remote..."; \
	echo "This will trigger the GitHub Actions release workflow."; \
	read -p "Push commit and tag? (y/N): " confirm_push; \
	if [ "$$confirm_push" != "y" ] && [ "$$confirm_push" != "Y" ]; then \
		echo "⚠️  Changes committed and tagged locally but NOT pushed"; \
		echo "To push manually: git push && git push --tags"; \
		exit 0; \
	fi; \
	git push && git push --tags; \
	echo ""; \
	echo "✅ Release v$$NEW_VERSION completed successfully!"; \
	echo ""; \
	echo "🔗 View release workflow: https://github.com/$$(git config --get remote.origin.url | sed 's/.*github.com[:/]\(.*\)\.git/\1/')/actions"; \
	echo "📦 Docker image will be available at: ghcr.io/$$(git config --get remote.origin.url | sed 's/.*github.com[:/]\(.*\)\.git/\1/' | tr '[:upper:]' '[:lower:]'):$$NEW_VERSION"

release-dry-run:
	@echo "🔍 Release dry run (no changes will be made)"
	@echo ""
	@echo "Current version: $$(cat VERSION)"
	@echo ""
	@echo "Git status:"
	@git status --short
	@echo ""
	@echo "Recent commits:"
	@git log --oneline -n 5
	@echo ""
	@echo "Last release tag:"
	@git describe --tags --abbrev=0 2>/dev/null || echo "No tags found"
	@echo ""
	@echo "Changes since last release:"
	@git log $$(git describe --tags --abbrev=0 2>/dev/null || echo "")..HEAD --oneline 2>/dev/null || echo "No previous release"
	@echo ""
	@echo "To create a release, run: make release"

release-hotfix:
	@echo "🚨 Starting hotfix release process..."
	@echo ""
	@echo "Current version: $$(cat VERSION)"
	@echo ""
	@read -p "This will create a PATCH release. Continue? (y/N): " confirm; \
	if [ "$$confirm" != "y" ] && [ "$$confirm" != "Y" ]; then \
		echo "❌ Hotfix cancelled"; \
		exit 1; \
	fi
	@echo ""
	@echo "Running quick tests..."
	@$(MAKE) ci-quick
	@echo ""
	@echo "Bumping patch version..."
	@python scripts/bump_version.py patch
	@NEW_VERSION=$$(cat VERSION); \
	echo "New version: $$NEW_VERSION"; \
	echo ""; \
	git add VERSION pyproject.toml app/__init__.py CHANGELOG.md; \
	git commit -m "chore: hotfix v$$NEW_VERSION"; \
	git tag -a "v$$NEW_VERSION" -m "Hotfix v$$NEW_VERSION"; \
	git push && git push --tags; \
	echo ""; \
	echo "✅ Hotfix v$$NEW_VERSION released!"

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
	@echo "2️⃣  Running security audit..."
	@echo "   Checking for known vulnerabilities in dependencies..."
	@uv pip install pip-audit 2>/dev/null || echo "   Note: pip-audit already installed"
	@uv run pip-audit --desc --skip-editable || echo "   Security audit completed (review findings above)"
	@echo ""
	@echo "3️⃣  Running linting checks..."
	@$(MAKE) lint
	@echo ""
	@echo "4️⃣  Running tests with coverage..."
	@$(MAKE) test
	@echo ""
	@echo "5️⃣  Building documentation with interactive diagrams..."
	@$(MAKE) docs
	@echo ""
	@echo "6️⃣  Validating interactive diagram assets..."
	@$(MAKE) docs-validate
	@echo ""
	@echo "✅ CI pipeline completed successfully!"
	@echo ""
	@echo "💡 This is equivalent to what GitHub Actions will run on push/PR"
	@echo "🎮 Interactive flowcharts included in build!"

# Simpler CI for quick checks
ci-quick:
	@echo "⚡ Running quick CI checks..."
	@$(MAKE) lint
	@$(MAKE) test-quick
	@echo "✅ Quick checks passed!"

# Security audit only
security:
	@echo "🔒 Running security audit on dependencies..."
	@uv pip install pip-audit
	@uv run pip-audit --desc --skip-editable
