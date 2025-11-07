# Versioning Guide

LOLStonks API Gateway follows [Semantic Versioning 2.0.0](https://semver.org/).

## Table of Contents

- [Semantic Versioning](#semantic-versioning)
- [Version Management](#version-management)
- [Release Process](#release-process)
- [Version Files](#version-files)
- [Automated Tools](#automated-tools)

## Semantic Versioning

Given a version number `MAJOR.MINOR.PATCH`, increment:

1. **MAJOR** version when you make incompatible API changes
2. **MINOR** version when you add functionality in a backward compatible manner
3. **PATCH** version when you make backward compatible bug fixes

### Version Format

```
2.0.0
│ │ │
│ │ └─ PATCH: Bug fixes, security patches, minor improvements
│ └─── MINOR: New features, new endpoints, non-breaking changes
└───── MAJOR: Breaking changes, API redesigns, major architecture changes
```

## Version Management

### Single Source of Truth

The project uses the `VERSION` file as the single source of truth for version numbers. All other files are updated from this file.

**Version Files:**
- `VERSION` - Primary version file (single source of truth)
- `pyproject.toml` - Python package version
- `app/__init__.py` - Runtime version accessible via `import app; app.__version__`
- `CHANGELOG.md` - Version history with dates

### When to Bump Versions

**MAJOR (Breaking Changes)**
```
Examples:
- Removing API endpoints
- Changing endpoint URLs or response formats
- Removing configuration options
- Changing authentication methods
- Incompatible database schema changes
```

**MINOR (New Features)**
```
Examples:
- Adding new API endpoints
- Adding new providers
- Adding new configuration options (with defaults)
- Adding new optional features
- Deprecating features (but not removing them)
```

**PATCH (Bug Fixes)**
```
Examples:
- Fixing bugs
- Security patches
- Performance improvements
- Documentation updates
- Dependency updates (patch versions)
```

## Release Process

### 1. Update Code and Tests

Make your changes and ensure all tests pass:

```bash
# Run tests
make test-full

# Run linting
make lint

# Check for security issues
make security-check
```

### 2. Update CHANGELOG.md

Add your changes to the `[Unreleased]` section:

```markdown
## [Unreleased]

### Added
- New feature description

### Fixed
- Bug fix description
```

See [Changelog Guide](./changelog-guide.md) for details.

### 3. Bump Version

Use the version bumping script:

```bash
# For patch release (2.0.0 -> 2.0.1)
python scripts/bump_version.py patch

# For minor release (2.0.0 -> 2.1.0)
python scripts/bump_version.py minor

# For major release (2.0.0 -> 3.0.0)
python scripts/bump_version.py major

# For specific version
python scripts/bump_version.py 2.5.0
```

This script will:
1. Update `VERSION` file
2. Update `pyproject.toml`
3. Update `app/__init__.py`
4. Move `[Unreleased]` changes to new version in `CHANGELOG.md`
5. Update version comparison links

### 4. Review Changes

Review all updated files:

```bash
git diff
```

Verify the changes in:
- `VERSION`
- `pyproject.toml`
- `app/__init__.py`
- `CHANGELOG.md`

### 5. Commit and Tag

Create a commit with the version bump:

```bash
# Commit the version bump
git add VERSION pyproject.toml app/__init__.py CHANGELOG.md
git commit -m "chore: bump version to 2.1.0"

# Create an annotated tag
git tag -a v2.1.0 -m "Release v2.1.0

Highlights:
- New feature A
- New feature B
- Bug fixes
"

# Push commits and tags
git push origin main
git push origin v2.1.0
```

### 6. Create GitHub Release

Create a GitHub release from the tag:

```bash
# Using GitHub CLI
gh release create v2.1.0 \
  --title "v2.1.0" \
  --notes "$(python scripts/extract_changelog.py 2.1.0)" \
  --latest
```

Or manually via GitHub web interface:
1. Go to Releases page
2. Click "Draft a new release"
3. Select the tag (e.g., `v2.1.0`)
4. Copy release notes from `CHANGELOG.md`
5. Publish release

### 7. Post-Release

After release:

```bash
# Verify the release
git describe --tags  # Should show v2.1.0

# Check PyPI upload (if applicable)
python -m build
python -m twine upload dist/*

# Announce the release
# - Update documentation site
# - Post in discussions
# - Notify users
```

## Version Files

### VERSION

Primary version file containing only the version number:

```
2.0.0
```

### pyproject.toml

Python package metadata:

```toml
[project]
name = "lolstonks-api-gateway"
version = "2.0.0"
```

### app/__init__.py

Runtime version accessible in code:

```python
"""LOLStonks API Gateway."""

__version__ = "2.0.0"
```

Usage:
```python
import app
print(f"Running version: {app.__version__}")
```

### CHANGELOG.md

Historical record of all changes:

```markdown
## [2.0.0] - 2024-11-06

### Added
- Multi-provider architecture
```

## Automated Tools

### bump_version.py

Automated version bumping script:

```bash
# Usage
python scripts/bump_version.py [major|minor|patch|VERSION]

# Examples
python scripts/bump_version.py patch    # 2.0.0 -> 2.0.1
python scripts/bump_version.py minor    # 2.0.0 -> 2.1.0
python scripts/bump_version.py major    # 2.0.0 -> 3.0.0
python scripts/bump_version.py 3.0.0   # Set to 3.0.0
```

### get_version.py

Get current version programmatically:

```bash
python scripts/get_version.py
# Output: 2.0.0

# Use in scripts
VERSION=$(python scripts/get_version.py)
echo "Building version $VERSION"
```

### Makefile Integration

Version management commands in Makefile:

```bash
# Get current version
make version

# Bump patch version
make version-bump-patch

# Bump minor version
make version-bump-minor

# Bump major version
make version-bump-major
```

## Pre-release Versions

For pre-release versions, use these conventions:

**Alpha:** `2.1.0-alpha.1`
```bash
python scripts/bump_version.py 2.1.0-alpha.1
```

**Beta:** `2.1.0-beta.1`
```bash
python scripts/bump_version.py 2.1.0-beta.1
```

**Release Candidate:** `2.1.0-rc.1`
```bash
python scripts/bump_version.py 2.1.0-rc.1
```

**Final Release:** `2.1.0`
```bash
python scripts/bump_version.py 2.1.0
```

## Version Checking in Code

### API Version Endpoint

The `/health` endpoint includes version information:

```bash
curl http://localhost:8080/health
```

```json
{
  "status": "healthy",
  "version": "2.0.0",
  "timestamp": "2024-11-06T12:00:00Z"
}
```

### Python Code

```python
from app import __version__

print(f"API Gateway v{__version__}")
```

### Docker Image Tags

Docker images are tagged with versions:

```bash
# Build with version
docker build -t lolstonks-api-gateway:2.0.0 .
docker build -t lolstonks-api-gateway:latest .

# Run specific version
docker run lolstonks-api-gateway:2.0.0
```

## Best Practices

1. **Never skip versions** - Don't jump from 2.0.0 to 2.2.0
2. **Always update CHANGELOG** - Keep users informed of changes
3. **Test before release** - Run full test suite before bumping version
4. **Tag releases** - Always create git tags for releases
5. **Semantic meaning** - Version numbers should communicate change impact
6. **Document breaking changes** - Clearly communicate MAJOR version changes
7. **Automate where possible** - Use scripts to reduce human error

## Migration Guides

For MAJOR version releases, create migration guides:

**Location:** `docs/migrations/v2-to-v3.md`

**Template:**
```markdown
# Migration Guide: v2.x to v3.0

## Breaking Changes

### Configuration Changes
- Old: `CACHE_TTL`
- New: `CACHE_TTL_DEFAULT`
- Action: Update your `.env` file

### API Endpoint Changes
- Removed: `/v1/summoner`
- Use instead: `/lol/summoner/v4/summoners`
- Action: Update your API calls

## New Features

### Provider System
- New configuration option: `ENABLED_PROVIDERS`
- See [Provider Guide](../api/providers.md) for details

## Upgrade Steps

1. Update environment variables
2. Update API client code
3. Test with new version
4. Deploy
```

## Questions?

- See [Semantic Versioning](https://semver.org/) specification
- Check [Changelog Guide](./changelog-guide.md) for related info
- Review past releases in `CHANGELOG.md` for examples
- Ask in team discussions for clarification
