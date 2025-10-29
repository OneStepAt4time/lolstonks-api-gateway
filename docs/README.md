# Documentation — LOLStonks API Gateway

Welcome to the comprehensive documentation for the LOLStonks API Gateway. This folder contains complete documentation built with MkDocs, including user guides, API reference, architecture documentation, and development resources.

## Documentation Structure

```
docs/
├── index.md                   # Homepage and project overview
├── getting-started/           # User guides and setup
│   ├── installation.md
│   ├── quick-start.md
│   └── configuration.md
├── api/                       # API reference (auto-generated)
│   ├── overview.md            # Comprehensive API overview
│   ├── riot-client.md         # Riot API client documentation
│   ├── models.md              # Pydantic models documentation
│   ├── routers.md             # API routers documentation
│   └── cache.md               # Caching system documentation
├── architecture/              # System architecture
│   ├── overview.md            # Architecture overview
│   ├── rate-limiting.md       # Rate limiting implementation
│   └── caching.md             # Caching strategy
├── development/               # Development documentation
│   ├── contributing.md        # Contribution guidelines
│   ├── testing.md             # Testing strategy
│   └── documentation.md       # Documentation guide
└── legacy/                    # Legacy documentation
    ├── api.md                 # Original API docs
    ├── setup.md               # Original setup guide
    ├── architecture.md        # Original architecture notes
    └── MODELS_STRUCTURE.md    # Model structure documentation
```

## Quick Start

### Prerequisites

```bash
# Install documentation dependencies
pip install -e ".[docs]"

# Or with uv
uv install --extra docs
```

### Local Development

```bash
# Serve documentation locally
mkdocs serve

# Or use the Makefile
make docs-serve
```

Visit http://127.0.0.1:8000 to view the documentation.

### Building Documentation

```bash
# Generate API docs and build
python scripts/generate_api_docs.py
mkdocs build

# Or use the Makefile
make docs
```

## Documentation Features

### Auto-Generated API Reference

The API reference section is automatically generated from Python docstrings using mkdocstrings:

- **Always in Sync**: Documentation is generated directly from source code
- **Cross-References**: Automatic linking between related documentation
- **Code Examples**: Included in docstrings and displayed in documentation
- **Type Information**: Automatic display of type hints and signatures
- **Source Code**: Option to view source code directly in documentation

### Comprehensive Coverage

- **User Guides**: Installation, quick start, and configuration
- **API Reference**: Complete auto-generated API documentation
- **Architecture**: System design, rate limiting, and caching strategy
- **Development**: Testing, contributing, and documentation guidelines
- **Legacy**: Preserved original documentation for reference

## Documentation Standards

The project follows these documentation standards:

- **Google Style Docstrings**: Consistent docstring format for auto-generation
- **Markdown Format**: All documentation written in Markdown
- **Semantic Structure**: Proper heading hierarchy and navigation
- **Code Examples**: Practical examples throughout the documentation
- **Cross-References**: Comprehensive linking between related content

## Deployment

Documentation is automatically deployed to GitHub Pages via GitHub Actions when pushed to the main branch. For local deployment:

```bash
# Deploy to GitHub Pages
mkdocs gh-deploy

# Or use the Makefile
make docs-deploy
```

## Contributing to Documentation

### Adding New Documentation

1. Create the markdown file in the appropriate directory
2. Follow the established style guidelines (see `development/documentation.md`)
3. Add cross-references to related content
4. Update the navigation in `mkdocs.yml`
5. Test locally with `mkdocs serve`
6. Submit a pull request

### Updating API Documentation

1. Update docstrings in the source code
2. Regenerate API documentation with `python scripts/generate_api_docs.py`
3. Review the generated documentation
4. Test the build process with `mkdocs build --strict`

## Development Workflow

```bash
# Complete development setup
make setup

# Format code and run quality checks
make format
make lint

# Run tests
make test

# Build and serve docs
make docs-serve

# Full CI pipeline locally
make ci
```

## Getting Help

For documentation issues:

1. Check existing [GitHub Issues](https://github.com/OneStepAt4time/lolstonks-api-gateway/issues)
2. Review the [Contributing Guide](development/contributing.md)
3. Check the [Documentation Guide](development/documentation.md) for style guidelines
4. Create a new issue with detailed description

## Tools and Technologies

- **MkDocs**: Static site generator
- **mkdocstrings**: Automatic API documentation from docstrings
- **Material for MkDocs**: Modern documentation theme
- **Mermaid**: Diagrams and visualizations
- **PyMdown Extensions**: Enhanced Markdown features

This documentation system provides a comprehensive, maintainable, and user-friendly documentation experience that stays synchronized with the codebase.
