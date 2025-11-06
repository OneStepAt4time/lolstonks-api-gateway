# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Changelog workflow and documentation

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
