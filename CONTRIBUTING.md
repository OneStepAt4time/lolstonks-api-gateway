# Contributing to LOLStonks API Gateway

Thank you for your interest in contributing! We appreciate all contributions, from bug reports to code improvements.

## Table of Contents

- [Quick Start](#quick-start)
- [Development Workflow](#development-workflow)
- [Git Flow Branching Strategy](#git-flow-branching-strategy)
- [Code Standards](#code-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Additional Resources](#additional-resources)

## Quick Start

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
git clone https://github.com/YOUR_USERNAME/lolstonks-api-gateway.git
cd lolstonks-api-gateway
```

### 2. Set Up Development Environment

```bash
# Install UV (if not already installed)
pip install uv

# Install dependencies
uv pip install -e ".[dev,docs]"

# Copy environment template
cp .env.example .env
# Edit .env and add your Riot API key
```

### 3. Verify Setup

```bash
# Run tests
make test-quick

# Run linter
make lint

# Start development server
make run
```

## Development Workflow

### 1. Understand the Branching Strategy

We use a modified Git Flow workflow. Please read [Git Flow Branching Strategy](docs/development/git-workflow.md) for complete details.

**Quick Reference**:
- `main` - Production-ready code
- `develop` - Integration branch (default)
- `feature/*` - New features
- `fix/*` - Bug fixes
- `hotfix/*` - Urgent production fixes

### 2. Create a Feature Branch

```bash
# Ensure you're on develop
git checkout develop
git pull origin develop

# Create a new feature branch
git checkout -b feature/your-feature-name
```

### 3. Make Your Changes

- Write clear, concise code
- Add type hints
- Include docstrings for functions
- Follow the project's code style

### 4. Test Your Changes

```bash
# Run quick tests
make test-quick

# Run full test suite
make test

# Check code quality
make lint
make format
```

### 5. Commit Your Changes

Follow [Conventional Commits](https://www.conventionalcommits.org/) format:

```bash
# Format: <type>: <description>
# Types: feat, fix, docs, style, refactor, test, chore

git add .
git commit -m "feat: add Tournament API router"
```

Examples:
- `feat: add rate limiting middleware`
- `fix: resolve Redis connection timeout`
- `docs: update API documentation`
- `test: add integration tests for caching`

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub using our [PR template](.github/pull_request_template.md).

## Git Flow Branching Strategy

For complete details on our Git Flow implementation, see [Git Workflow Documentation](docs/development/git-workflow.md).

### Key Points

1. **Branch from `develop`** for features and fixes
2. **Branch from `main`** for hotfixes only
3. **Merge to `develop`** for features and fixes
4. **Merge to `main`** via release process only
5. **Delete branches** after merge

### Branch Naming

- `feature/<feature-name>` - New features
- `fix/<bug-description>` - Bug fixes
- `hotfix/<urgent-fix>` - Production hotfixes
- `refactor/<description>` - Code refactoring
- `docs/<description>` - Documentation changes
- `test/<description>` - Test improvements

## Code Standards

### Python Style

- Follow [PEP 8](https://pep8.org/) style guide
- Use [Ruff](https://docs.astral.sh/ruff/) for linting
- Maximum line length: 100 characters
- Use type hints for all functions
- Use [loguru](https://github.com/Delgan/loguru) for logging (never `print()`)

### Documentation

- Use docstrings for all modules, classes, and functions
- Follow [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- Update API docs for endpoint changes
- Update CHANGELOG.md for user-facing changes

### Code Quality

Before committing:
```bash
make format    # Format code with ruff
make lint      # Check for linting errors
make test-quick  # Run tests
```

## Testing Guidelines

### Test Coverage

- Maintain >80% test coverage
- Add tests for new features
- Update tests for bug fixes
- Use pytest for all tests

### Test Structure

```
tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
└── conftest.py     # Shared fixtures
```

### Writing Tests

```python
# Use descriptive test names
def test_tournament_api_returns_404_for_invalid_tournament_code():
    # Arrange
    client = TestClient(app)
    tournament_code = "INVALID"

    # Act
    response = client.get(f"/api/tournament/{tournament_code}")

    # Assert
    assert response.status_code == 404
```

### Running Tests

```bash
# Quick tests (development)
make test-quick

# Full test suite
make test

# With coverage
make test-cov

# Specific test file
uv run pytest tests/test_rate_limiter.py -v
```

## Pull Request Process

### Before Creating PR

1. **Update documentation** if needed
2. **Add/update tests** for your changes
3. **Run full test suite** and ensure all tests pass
4. **Update CHANGELOG.md** for user-facing changes
5. **Rebase with develop** to resolve conflicts

```bash
git checkout develop
git pull origin develop
git checkout feature/your-feature-name
git rebase develop
```

### Creating PR

1. Fill out the PR template completely
2. Link related issues
3. Request review from maintainers
4. Ensure CI checks pass

### PR Review Process

1. **Address feedback** promptly
2. **Update PR** based on review
3. **Request re-review** if needed
4. **Merge** after approval

### After Merge

1. **Delete your branch**:
   ```bash
   git branch -d feature/your-feature-name
   git push origin --delete feature/your-feature-name
   ```

2. **Update local develop**:
   ```bash
   git checkout develop
   git pull origin develop
   ```

## Additional Resources

### Documentation

- [Full Contributing Guide](https://onestepat4time.github.io/lolstonks-api-gateway/development/contributing/)
- [Git Workflow](docs/development/git-workflow.md)
- [API Documentation](docs/api/)
- [Architecture](docs/architecture/)

### Community

- [GitHub Discussions](https://github.com/OneStepAt4time/lolstonks-api-gateway/discussions)
- [Issues](https://github.com/OneStepAt4time/lolstonks-api-gateway/issues)
- [Security Policy](.github/SECURITY.md)

### Tools

- [UV Documentation](https://docs.astral.sh/uv/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Pydantic Docs](https://docs.pydantic.dev/)
- [pytest Docs](https://docs.pytest.org/)

## Types of Contributions

We welcome all types of contributions:

- Bug Reports - Help us identify issues
- Feature Requests - Suggest new functionality
- Code Contributions - Fix bugs or implement features
- Documentation - Improve guides and examples
- Test Improvements - Add or improve tests
- Code Reviews - Help review pull requests

## Getting Help

If you need help:
1. Check existing [Issues](https://github.com/OneStepAt4time/lolstonks-api-gateway/issues)
2. Start a [Discussion](https://github.com/OneStepAt4time/lolstonks-api-gateway/discussions)
3. Read the [Documentation](https://onestepat4time.github.io/lolstonks-api-gateway/)

---

Thank you for contributing to LOLStonks API Gateway!
