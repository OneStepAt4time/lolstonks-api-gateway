# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- **Documentation Mermaid diagrams**: Fixed syntax errors in architecture documentation diagrams
  - **HTML entities**: Fixed HTML entities (`&lt;`, `&gt;`, `&amp;`) that were causing rendering errors
    - `docs/architecture/data-flow.md`: Fixed 3 HTML entities in timing annotations
    - `docs/architecture/system-overview.md`: Fixed 3 HTML entities in flow annotations
  - **Special characters**: Added quotes around Mermaid labels containing `<` or `>` characters to prevent syntax errors
    - `docs/architecture/routing.md`: Fixed label with `<10ms` timing annotation by wrapping in quotes
- **Spectator endpoint parameter**: Changed from `puuid` to `encryptedPUUID` to match Riot API specification
- **Clash endpoint clarification**: Confirmed `/lol/clash/v1/players/by-puuid/{puuid}` is correct (Riot deprecated `/by-summoner/` variant during PUUID migration)
- **Windows async test compatibility**: Added event loop policy fix for Windows platform in conftest.py

### Added
- **Comprehensive integration test suite**: 83 tests across 4 modules with 69% code coverage
  - `tests/integration/test_endpoints.py`: 28 tests for all 12 required API endpoints
  - `tests/integration/test_caching.py`: 11 tests for cache behavior (hit/miss, TTL, force refresh)
  - `tests/integration/test_regional_routing.py`: 19 tests for platform and game region routing
  - `tests/integration/test_pagination.py`: 25 tests for pagination across League, Match, and Mastery APIs
- Changelog workflow and documentation
- **Dependency vulnerability scanning**: pip-audit integration in CI workflow for automatic dependency security checks
- **Dependabot configuration**: Automated dependency updates for Python, GitHub Actions, and Docker
- **Docker image scanning**: Trivy security scanner for container vulnerability detection
- **SARIF uploads**: Security scan results uploaded to GitHub Security tab
- **Post-deployment health checks**: Automated verification of Docker images after build
- **Production approval gates**: Manual approval requirement for production releases via GitHub Environments
- **Release approval documentation**: Comprehensive guide for setting up and using production approval gates
- **Release notification automation**: Slack, Discord, and Microsoft Teams webhook support for release notifications
- **Automated release script**: `make release` command for interactive release process
- **Release dry-run command**: `make release-dry-run` to preview release without making changes
- **Hotfix release command**: `make release-hotfix` for quick patch releases
- **Rollback procedures documentation**: Comprehensive rollback guides for Docker and git-based deployments
- **Emergency rollback scripts**: Automated rollback scripts for both Docker and systemd deployments

### Changed
- CI workflow now includes dependency security audits
- Release workflows enhanced with vulnerability scanning and health checks
- Production release workflow requires manual approval before deployment
- Makefile help text updated with new release commands
- Version command updated to read from VERSION file directly

### Fixed
- Docker image repository names now converted to lowercase to comply with GitHub Container Registry requirements

### Security
- Added automated dependency vulnerability scanning with pip-audit
- Added container image vulnerability scanning with Trivy
- Security scan results now uploaded to GitHub Security tab for tracking
- Production releases now require manual approval for additional oversight

## [2.0.0] - 2025-11-06

### Added
- **Multi-Provider Architecture**: Support for three data providers
  - Riot Games API for live game data
  - Data Dragon CDN for official static data
  - Community Dragon for enhanced static data and assets
- **Provider System**: BaseProvider abstraction layer for easy provider integration
- **Provider Registry**: Singleton pattern for managing provider instances
- **76+ API Endpoints**: Complete coverage across all three data providers
- **API Key Rotation**: Round-robin distribution across multiple Riot API keys
- **Enhanced Security**: Real-time security monitoring and status endpoints
- **Error Monitoring Middleware**: Comprehensive error tracking with structured logging
- **Health Monitoring**: Multi-provider health checks with detailed status
- **Centralized Cache Helpers**: `fetch_with_cache` utility for consistent caching
- **Provider Configuration**: `ENABLED_PROVIDERS` setting to enable/disable providers
- **Data Dragon Router**: Complete static data endpoints (/ddragon/*)
- **Community Dragon Router**: Enhanced static data endpoints (/cdragon/*)
- **TFT Support**: Teamfight Tactics data through Community Dragon
- **Monitoring Endpoints**: System metrics, performance, and observability
- **Security Router**: Security status and monitoring endpoints
- **Provider Documentation**: Complete provider architecture and usage docs
- **Security Documentation**: Comprehensive security guide and best practices

### Changed
- **Health Endpoint**: Now reports status for all registered providers
- **Cache Strategy**: Optimized TTL settings per endpoint type
- **Configuration**: Expanded with provider-specific settings
- **Error Handling**: Enhanced with structured logging and monitoring
- **Documentation**: Complete overhaul with v2.0 feature coverage

### Fixed
- API key validation handling for empty strings from environment
- Cache key generation for consistent cache behavior
- Provider initialization order and dependency management
- Test suite compatibility with new provider system

## [1.0.0] - 2025-10-15

### Added
- Initial release of LOLStonks API Gateway
- FastAPI-based async architecture
- Redis caching with configurable TTL
- Token bucket rate limiting
- Automatic retry on 429 responses
- Multi-region support for Riot API
- Core Riot API endpoints:
  - Account (ACCOUNT-V1)
  - Summoner (SUMMONER-V4)
  - Match (MATCH-V5)
  - League (LEAGUE-V4)
  - Champion Mastery (CHAMPION-MASTERY-V4)
  - Challenges (CHALLENGES-V1)
  - Clash (CLASH-V1)
  - Champion Rotation (CHAMPION-V3)
  - Spectator (SPECTATOR-V5)
  - Platform Status (LOL-STATUS-V4)
- Docker Compose deployment support
- Comprehensive test suite
- Interactive API documentation (Swagger UI)
- Environment-based configuration
- Match tracking system

### Security
- Input validation with Pydantic models
- Rate limit protection
- API key configuration via environment variables

[Unreleased]: https://github.com/OneStepAt4time/lolstonks-api-gateway/compare/v2.0.0...HEAD
[2.0.0]: https://github.com/OneStepAt4time/lolstonks-api-gateway/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/OneStepAt4time/lolstonks-api-gateway/releases/tag/v1.0.0
