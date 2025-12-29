# CI Verification Guide

This guide explains how to run CI checks locally before pushing to avoid GitHub Actions failures.

## Overview

The CI pipeline runs the following checks:
1. **Security Audit** - Scans dependencies for known vulnerabilities (using pip-audit)
2. **Linting** - Code quality checks with ruff (formatting + lint rules)
3. **Type Checking** - Static type analysis with mypy
4. **Testing** - Unit and integration tests with pytest + coverage
5. **Documentation Build** - Validates MkDocs structure and generates API docs

## Running CI Locally

### Quick CI (Fast Checks)

For rapid iteration during development:

```bash
make ci-quick
```

This runs:
- Ruff linting (format + check)
- Quick tests (no coverage)

**Time**: ~30 seconds

### Full CI (Complete Pipeline)

Before pushing to GitHub:

```bash
make ci
```

This runs:
1. Security audit (pip-audit)
2. Ruff linting (format + check)
3. Full test suite with coverage
4. Documentation build with validation
5. Interactive diagram validation

**Time**: ~2-3 minutes

### Individual Checks

Run specific checks as needed:

```bash
# Security audit only
make security

# Linting only
make lint

# Tests with coverage
make test

# Quick tests (no coverage)
make test-quick

# Documentation build
make docs

# Documentation validation
make docs-validate
```

## Common Issues and Solutions

### Security Vulnerabilities Found

If pip-audit finds vulnerabilities:

```bash
# Check what's vulnerable
make security

# Update specific package
uv pip install "package>=fixed.version" --upgrade
uv lock --upgrade-package package

# Example: Fix urllib3 vulnerability
uv pip install "urllib3>=2.6.0" --upgrade
uv lock --upgrade-package urllib3
```

### Linting Errors

```bash
# Auto-fix most issues
make format

# Check remaining issues
make lint

# Fix specific file
uv run ruff check --fix app/main.py
uv run ruff format app/main.py
```

### Test Failures

```bash
# Run specific test file
uv run pytest tests/test_main.py -v

# Run with verbose output
uv run pytest -v --tb=short

# Run only unit tests
uv run pytest tests/unit/ -v

# Run only integration tests
uv run pytest tests/integration/ -v

# Skip slow tests
uv run pytest -m "not slow"
```

### Documentation Build Errors

```bash
# Validate documentation structure
make docs-validate

# Check specific errors
uv run mkdocs build --strict

# Serve locally to debug
make docs-serve
```

## GitHub Actions Workflow Files

The CI pipeline is defined in `.github/workflows/`:

- **ci.yml** - Main CI pipeline (runs on push to main/develop, and PRs)
- **docs.yml** - Documentation deployment to GitHub Pages
- **docs-verification.yml** - Playwright-based documentation testing

### CI Environment Variables

GitHub Actions uses these secrets:

- `REDIS_HOST` - Redis server host (defaults to localhost)
- `REDIS_PORT` - Redis server port (defaults to 6379)
- `RIOT_API_KEY` - Riot Games API key (for integration tests)

Local tests use mock values from `tests/conftest.py`.

## Pre-Push Checklist

Before pushing code:

1. **Security check**
   ```bash
   make security
   ```
   Review any vulnerabilities and update if needed.

2. **Code quality**
   ```bash
   make format && make lint
   ```
   Ensure no linting errors.

3. **Tests**
   ```bash
   make test-quick
   ```
   All tests should pass.

4. **Full CI** (optional but recommended)
   ```bash
   make ci
   ```

5. **Commit**
   ```bash
   git add .
   git commit -m "feat: your changes"
   ```

6. **Push**
   ```bash
   git push
   ```

## CI Best Practices

### During Development

- Use `make ci-quick` for rapid feedback
- Run `make format` before committing
- Fix test failures immediately

### Before Pushing

- Always run `make ci` or at least `make ci-quick`
- Check security audit output for vulnerabilities
- Ensure documentation builds successfully

### For Pull Requests

- Run full `make ci` before creating PR
- Include test coverage for new features
- Update documentation for API changes

### For Hotfixes

- Use `make ci-quick` for faster iteration
- Focus on fixing the immediate issue
- Follow up with full CI after merge

## Troubleshooting

### CI Passes Locally but Fails on GitHub

1. **Check Python version**
   ```bash
   # CI uses Python 3.13
   python --version  # Should be 3.13.x
   ```

2. **Check dependency versions**
   ```bash
   uv sync --extra dev  # Fresh sync
   ```

3. **Check environment variables**
   - CI uses specific Redis settings
   - Some tests may behave differently without real Redis

4. **Check platform differences**
   - CI runs on Linux (ubuntu-latest)
   - Local development may be on Windows/macOS
   - File paths and line endings can differ

### Intermittent Test Failures

1. **Redis connection issues**
   ```bash
   docker ps | grep redis  # Check if Redis is running
   make redis-start        # Start Redis if needed
   ```

2. **Event loop issues** (Windows)
   - Already handled by `tests/conftest.py`
   - Ensure you're using pytest fixtures correctly

3. **Rate limiting** (Riot API tests)
   - Tests use mocks, no real API calls
   - Check you're not accidentally hitting real API

### Documentation Verification Fails

The `docs-verification.yml` workflow uses Playwright to test documentation:

```bash
# Run locally (requires Playwright browsers)
uv sync --extra test-docs
uv run playwright install chromium
uv run pytest tests/docs_verification/ --env=prod
```

Common issues:
- **Port conflicts**: Ensure port 8000 is available
- **Missing browsers**: Run `playwright install chromium`
- **Base URL conflicts**: Check for pytest option conflicts in conftest.py

## CI Metrics

Target metrics for healthy CI:

| Metric | Target |
|--------|--------|
| Test Coverage | >80% |
| Linting | 0 errors, 0 warnings |
| Security | 0 known vulnerabilities |
| CI Duration | <5 minutes |
| Test Duration | <2 minutes |

## Related Documentation

- [Development Guide](../development/index.md) - General development patterns
- [Testing Guide](testing.md) - Testing strategies and conventions
- [Git Workflow](git-workflow.md) - Branching and commit standards

## Getting Help

If CI fails and you can't resolve it:

1. Check the GitHub Actions logs for detailed error messages
2. Compare with local `make ci` output
3. Check recent commits for breaking changes
4. Ask for help in team channels with:
   - The error message
   - The workflow that failed
   - Steps you've already tried
