# Changelog Guide

This project follows the [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Table of Contents

- [When to Update the Changelog](#when-to-update-the-changelog)
- [Changelog Format](#changelog-format)
- [Change Categories](#change-categories)
- [Writing Good Changelog Entries](#writing-good-changelog-entries)
- [Release Process](#release-process)
- [Automated Checks](#automated-checks)

## When to Update the Changelog

Update `CHANGELOG.md` whenever you make changes that affect users or developers of the project:

**Always update:**
- ✅ New features or functionality
- ✅ Bug fixes
- ✅ Breaking changes
- ✅ Deprecations
- ✅ Security fixes
- ✅ Performance improvements
- ✅ API changes

**May skip (use `skip-changelog` label):**
- ⏭️ Documentation-only changes
- ⏭️ Internal refactoring with no external impact
- ⏭️ Test updates without behavior changes
- ⏭️ CI/CD configuration changes
- ⏭️ Development tooling updates

## Changelog Format

The changelog uses the following structure:

```markdown
## [Unreleased]

### Added
- New feature description

### Changed
- Modified feature description

### Deprecated
- Soon-to-be removed feature description

### Removed
- Removed feature description

### Fixed
- Bug fix description

### Security
- Security improvement description
```

## Change Categories

### Added
New features or capabilities.

**Examples:**
```markdown
- **Multi-Provider Support**: Integration with Data Dragon and Community Dragon
- **API Key Rotation**: Round-robin distribution across multiple API keys
- **TFT Endpoints**: Teamfight Tactics data through `/cdragon/tft/*`
```

### Changed
Changes to existing functionality that don't break compatibility.

**Examples:**
```markdown
- **Cache TTL**: Optimized default TTL values for better performance
- **Health Check**: Now includes provider-specific status information
- **Logging**: Enhanced with structured JSON format and request tracing
```

### Deprecated
Features that will be removed in upcoming releases.

**Examples:**
```markdown
- **Single API Key**: Use `RIOT_API_KEYS` instead of `RIOT_API_KEY` (will be removed in v3.0)
- **Legacy Endpoints**: `/v1/summoner` endpoints deprecated in favor of `/lol/summoner/v4`
```

### Removed
Features that have been removed.

**Examples:**
```markdown
- **Legacy Cache Backend**: Removed in-memory cache option
- **Deprecated Endpoints**: Removed `/v1/*` endpoints (use `/lol/*/v4` instead)
```

### Fixed
Bug fixes.

**Examples:**
```markdown
- **Rate Limiter**: Fixed race condition in token bucket implementation
- **Cache Keys**: Corrected cache key generation for multi-region requests
- **Memory Leak**: Resolved HTTP client connection pooling issue
```

### Security
Security improvements and vulnerability fixes.

**Examples:**
```markdown
- **Input Validation**: Added Pydantic validation for all endpoint parameters
- **API Key Storage**: Improved secure handling of API keys in configuration
- **Dependencies**: Updated httpx to 0.25.0 to address CVE-2023-XXXXX
```

## Writing Good Changelog Entries

### Be Specific

❌ **Bad:**
```markdown
- Fixed bugs
- Improved performance
- Updated code
```

✅ **Good:**
```markdown
- Fixed race condition in rate limiter causing 429 errors under high load
- Improved cache hit rate by 40% through optimized TTL configuration
- Updated Riot API client to handle new regional routing
```

### Use Bold for Main Topic

```markdown
- **Provider System**: Added abstraction layer for data providers
- **API Endpoints**: Expanded coverage to 76+ endpoints
- **Documentation**: Complete overhaul with v2.0 features
```

### Include Context

```markdown
- **Breaking Change - Configuration**: Renamed `CACHE_TTL` to `CACHE_TTL_DEFAULT` for clarity
  - Migration: Update your `.env` file to use the new variable name
  - Old configurations will be supported until v3.0
```

### Group Related Changes

```markdown
- **Provider Architecture**:
  - Added BaseProvider abstraction interface
  - Implemented ProviderRegistry for provider management
  - Created provider-specific routers for Data Dragon and Community Dragon
```

## Release Process

### 1. Update Version Numbers

When preparing a release, move items from `[Unreleased]` to a new version section:

```markdown
## [Unreleased]

## [2.1.0] - 2024-11-15

### Added
- Feature that was in unreleased
```

### 2. Add Version Links

Update the comparison links at the bottom:

```markdown
[Unreleased]: https://github.com/OneStepAt4time/lolstonks-api-gateway/compare/v2.1.0...HEAD
[2.1.0]: https://github.com/OneStepAt4time/lolstonks-api-gateway/compare/v2.0.0...v2.1.0
```

### 3. Semantic Versioning

Choose version numbers based on the changes:

- **MAJOR (3.0.0)**: Breaking changes
  - API endpoint removals
  - Incompatible configuration changes
  - Major architecture changes

- **MINOR (2.1.0)**: New features, no breaking changes
  - New endpoints
  - New providers
  - New configuration options (with defaults)

- **PATCH (2.0.1)**: Bug fixes, no breaking changes
  - Bug fixes
  - Security patches
  - Performance improvements

### 4. Create Release

After updating the changelog:

```bash
# Tag the release
git tag -a v2.1.0 -m "Release v2.1.0"

# Push the tag
git push origin v2.1.0
```

## Automated Checks

### GitHub Actions Workflow

The project includes a GitHub Actions workflow (`.github/workflows/changelog.yml`) that:

1. **Checks PRs**: Verifies that `CHANGELOG.md` is updated in pull requests
2. **Allows Skip**: PRs labeled `skip-changelog` bypass the check
3. **Blocks Merge**: PRs without changelog updates (and without skip label) cannot merge

### Skipping the Check

For documentation-only or internal changes, add the `skip-changelog` label to your PR:

```bash
# Via GitHub CLI
gh pr edit <PR_NUMBER> --add-label skip-changelog
```

Or add the label through the GitHub web interface.

## Examples

### Example: New Feature

```markdown
## [Unreleased]

### Added
- **GraphQL API**: New GraphQL endpoint at `/graphql` for flexible data queries
  - Supports all Riot API endpoints
  - Includes Data Dragon static data
  - Auto-generated schema from Pydantic models
```

### Example: Breaking Change

```markdown
## [Unreleased]

### Changed
- **BREAKING: Configuration Format**: Environment variables now use `LOLSTONKS_` prefix
  - Migration: Add `LOLSTONKS_` prefix to all environment variables
  - Example: `RIOT_API_KEY` → `LOLSTONKS_RIOT_API_KEY`
  - Old format will be removed in v3.0.0
```

### Example: Bug Fix with Context

```markdown
## [Unreleased]

### Fixed
- **Rate Limiter**: Fixed token bucket exhaustion under sustained high load
  - Issue: Rate limiter would occasionally allow requests to exceed configured limits
  - Impact: Could result in 429 errors from Riot API
  - Resolution: Improved thread-safe token acquisition logic
  - Related: #123, #145
```

## Best Practices

1. **Update as You Code**: Add changelog entries with your code changes, not at release time
2. **User Perspective**: Write from the user's point of view, not implementation details
3. **Group Logically**: Keep related changes together
4. **Link Issues**: Reference GitHub issues when relevant
5. **Be Honest**: Don't hide breaking changes or known issues
6. **Review History**: Check `git log --oneline` for changes you might have missed

## Tools

### Generate Changelog from Git History

Quick script to extract recent commits:

```bash
# Get commits since last release
git log v2.0.0..HEAD --pretty=format:"- %s" --reverse
```

### Validate Changelog Format

The project includes a changelog validation script:

```bash
# Check changelog format (future addition)
python scripts/validate_changelog.py
```

## Questions?

- See [Keep a Changelog](https://keepachangelog.com/) for the full specification
- Check [Semantic Versioning](https://semver.org/) for version numbering rules
- Review past releases in `CHANGELOG.md` for examples
- Ask in team discussions or GitHub issues for clarification
