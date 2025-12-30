# Contributing

Thank you for your interest in contributing to LOLStonks API Gateway! This guide will help you get started with contributing to the project.

## Code of Conduct

By participating in this project, you agree to be respectful, inclusive, and constructive in all interactions. We expect contributors to:

- Be respectful of differing viewpoints and experiences
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

## Ways to Contribute

There are many ways to contribute to this project:

- **Report bugs**: Submit detailed bug reports with reproduction steps
- **Suggest features**: Propose new features or enhancements
- **Improve documentation**: Fix typos, clarify instructions, or add examples
- **Submit code**: Fix bugs or implement new features
- **Review pull requests**: Help review and test other contributors' code

## Getting Started

### Development Environment Setup

1. **Fork and clone the repository**:

```bash
git clone https://github.com/YOUR_USERNAME/lolstonks-api-gateway.git
cd lolstonks-api-gateway
```

2. **Install dependencies**:

```bash
# Using UV (recommended)
uv pip install -e ".[dev,docs]"

# Or using pip
pip install -e ".[dev,docs]"
```

3. **Set up environment variables**:

```bash
cp .env.example .env
# Edit .env and add your Riot API key
```

4. **Start Redis** (required for development):

```bash
# Using Docker
docker-compose up -d redis

# Or install Redis locally
```

5. **Run the development server**:

```bash
python -m app.main
```

### Project Structure

```
lolstonks-api-gateway/
├── app/
│   ├── main.py              # Application entry point
│   ├── config.py            # Configuration management
│   ├── routers/             # API endpoint routers
│   ├── riot/                # Riot API client and rate limiting
│   ├── cache/               # Caching and match tracking
│   └── models/              # Data models
├── docs/                    # Documentation source
├── tests/                   # Test suite
└── scripts/                 # Utility scripts
```

## Development Workflow

### Git Flow Branching Strategy

This project follows **Git Flow** branching strategy. Please read [Git Flow Branching Strategy](git-workflow.md) for complete details.

**Branch Structure**:
- `main` - Production-ready code (always deployable)
- `develop` - Integration branch for all features
- `feature/*` - New features (branch from `develop`)
- `fix/*` - Bug fixes (branch from `develop`)
- `hotfix/*` - Urgent production fixes (branch from `main`)
- `refactor/*` - Code refactoring (branch from `develop`)
- `docs/*` - Documentation changes (branch from `develop`)
- `test/*` - Test additions (branch from `develop`)

### 1. Create a Branch

**For new features or bug fixes**, branch from `develop`:

```bash
# Ensure you're on develop
git checkout develop
git pull origin develop

# Create a feature branch
git checkout -b feature/your-feature-name

# Or create a fix branch
git checkout -b fix/your-bug-fix
```

**For urgent production fixes**, branch from `main`:

```bash
git checkout main
git pull origin main
git checkout -b hotfix/urgent-fix
```

### 2. Make Your Changes

- Follow the existing code style and patterns
- Write clear, concise commit messages
- Keep changes focused and atomic
- Add tests for new functionality
- Update documentation as needed

### 3. Test Your Changes

Before submitting, ensure your changes pass all checks:

```bash
# Run tests (when available)
pytest

# Run type checking (if configured)
mypy app

# Run linting (if configured)
ruff check app
```

### 4. Commit Your Changes

Write clear commit messages following this format:

```bash
git commit -m "feat: add support for new Riot API endpoint"
git commit -m "fix: resolve rate limiting issue with burst requests"
git commit -m "docs: update installation instructions"
```

**Commit message format**:
- Use present tense ("add feature" not "added feature")
- Use imperative mood ("move cursor to..." not "moves cursor to...")
- Limit first line to 72 characters
- Reference issues and pull requests when relevant

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

**Pull Request Guidelines**:
- **Target branch**: `develop` for `feature/*`, `fix/*`, `refactor/*`, `docs/*`, `test/*` branches
- **Target branch**: `main` for `hotfix/*` branches (must also be merged to `develop`)
- Include clear title and description
- Reference related issues
- Ensure all CI checks pass
- Get at least one maintainer approval

Then open a pull request on GitHub with:

- Clear title describing the change
- Detailed description of what changed and why
- Reference to any related issues
- Screenshots or examples if applicable

## Code Style Guidelines

### Python Style

- Follow PEP 8 guidelines
- Use type hints for function parameters and return values
- Write docstrings for all public functions and classes
- Keep functions focused and single-purpose
- Use meaningful variable and function names

**Example**:

```python
from typing import Optional

async def get_summoner_by_name(
    summoner_name: str,
    region: str = "euw1"
) -> Optional[dict]:
    """
    Retrieve summoner information by name.

    Args:
        summoner_name: The summoner's in-game name
        region: The game region (default: euw1)

    Returns:
        Summoner data dictionary or None if not found
    """
    # Implementation here
    pass
```

### Documentation Style

- Use clear, concise language
- Include code examples for complex features
- Keep line length reasonable (80-100 characters)
- Use proper markdown formatting
- Avoid jargon and explain technical terms

## Testing Guidelines

### Writing Tests

- Write tests for all new functionality
- Ensure tests are isolated and reproducible
- Use descriptive test names
- Test both success and failure cases
- Mock external API calls

**Example test structure**:

```python
import pytest
from app.riot.client import RiotClient

@pytest.mark.asyncio
async def test_get_summoner_by_name_success():
    """Test successful summoner retrieval."""
    client = RiotClient(api_key="test-key")
    # Test implementation
    pass

@pytest.mark.asyncio
async def test_get_summoner_by_name_not_found():
    """Test summoner not found scenario."""
    # Test implementation
    pass
```

## Documentation Guidelines

### Updating Documentation

When making changes that affect documentation:

1. Update relevant `.md` files in the `docs/` directory
2. Test documentation locally:

```bash
mkdocs serve
```

3. Ensure all links work correctly
4. Add code examples for new features
5. Update API reference if endpoints change

### Documentation Structure

- **Getting Started**: Installation and quick start guides
- **API Reference**: Endpoint documentation
- **Architecture**: System design and component documentation
- **Development**: Contributing and development guides
- **Operations**: Deployment and maintenance guides

## Pull Request Process

1. **Before submitting**:
   - Ensure all tests pass
   - Update documentation
   - Rebase on latest main/develop
   - Resolve any merge conflicts

2. **PR requirements**:
   - Clear description of changes
   - Link to related issue (if applicable)
   - Tests pass and coverage maintained
   - Documentation updated
   - Code reviewed by at least one maintainer

3. **After submission**:
   - Respond to review comments
   - Make requested changes
   - Keep PR updated with main branch
   - Be patient and respectful

## Issue Reporting

### Bug Reports

When reporting bugs, include:

- Clear, descriptive title
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details (OS, Python version, etc.)
- Error messages and stack traces
- Relevant logs

**Example**:

```markdown
## Bug Description
Rate limiter fails under high concurrent load

## Steps to Reproduce
1. Start gateway with default configuration
2. Send 100 concurrent requests
3. Observe rate limit errors

## Expected Behavior
All requests should be properly rate limited

## Actual Behavior
Some requests bypass rate limiter

## Environment
- Python: 3.12.0
- OS: Ubuntu 22.04
- Redis: 7.0.5
```

### Feature Requests

When suggesting features, include:

- Clear description of the feature
- Use case and motivation
- Proposed implementation (optional)
- Potential impact on existing functionality

## Contributor License Agreement

By contributing to this repository, you agree that:

- Your contributions will be licensed under the MIT License
- You have the right to contribute the code/documentation
- You understand your contributions may be modified or rejected

## Getting Help

If you need help with contributing:

- Check existing documentation
- Search existing issues and pull requests
- Open a discussion on GitHub
- Ask questions in pull request comments

## Recognition

All contributors will be recognized in the project. Significant contributions may be highlighted in release notes.

## Additional Resources

- [GitHub Flow Guide](https://guides.github.com/introduction/flow/)
- [Writing Good Commit Messages](https://chris.beams.io/posts/git-commit/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

Thank you for contributing to LOLStonks API Gateway!
