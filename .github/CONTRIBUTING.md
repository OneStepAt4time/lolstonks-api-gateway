# Contributing to LOLStonks API Gateway

Thank you for your interest in contributing! We appreciate all contributions, from bug reports to code improvements.

## Quick Links

- **📚 [Full Contributing Guide](https://onestepat4time.github.io/lolstonks-api-gateway/development/contributing/)** - Complete documentation on how to contribute
- **📖 [Code of Conduct](CODE_OF_CONDUCT.md)** - Community guidelines
- **🔒 [Security Policy](SECURITY.md)** - How to report security vulnerabilities

## Quick Start

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/lolstonks-api-gateway.git
cd lolstonks-api-gateway
```

### 2. Install Dependencies

```bash
# Using UV (recommended)
uv pip install -e ".[dev,docs]"

# Or using pip
pip install -e ".[dev,docs]"
```

### 3. Set Up Environment

```bash
cp .env.example .env
# Edit .env and add your Riot API key
```

### 4. Run Tests

```bash
pytest
```

### 5. Make Changes

- Create a feature branch: `git checkout -b feature/your-feature-name`
- Make your changes
- Run tests and linters: `make lint && make test`
- Commit with clear messages
- Push and create a Pull Request

## Development Workflow

1. **Issues First**: For major changes, open an issue first to discuss
2. **Code Quality**: Follow the project's coding standards
3. **Testing**: Add tests for new features
4. **Documentation**: Update docs for user-facing changes
5. **Pre-commit Hooks**: Install and use pre-commit hooks

```bash
uv run pre-commit install
```

## Pull Request Process

1. Update documentation if needed
2. Ensure all tests pass
3. Update the changelog if applicable
4. Request review from maintainers
5. Address feedback promptly

## Need Help?

- **Questions?** Open a [Discussion](https://github.com/OneStepAt4time/lolstonks-api-gateway/discussions)
- **Bug?** Open an [Issue](https://github.com/OneStepAt4time/lolstonks-api-gateway/issues)
- **Documentation?** See the [full docs](https://onestepat4time.github.io/lolstonks-api-gateway/)

## Types of Contributions

- 🐛 **Bug Reports** - Help us identify issues
- ✨ **Feature Requests** - Suggest new functionality
- 📝 **Documentation** - Improve guides and examples
- 🔧 **Code** - Fix bugs or implement features
- 👀 **Reviews** - Help review pull requests

---

For complete details, please read the **[Full Contributing Guide](https://onestepat4time.github.io/lolstonks-api-gateway/development/contributing/)**.
