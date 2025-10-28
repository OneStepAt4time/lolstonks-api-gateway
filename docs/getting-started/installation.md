# Installation

This guide covers different installation methods for the LOLStonks API Gateway.

## Prerequisites

- **Python 3.12+** - The gateway requires Python 3.12 or higher
- **Redis Server** - Required for caching and match tracking
- **Riot Developer API Key** - Get one at [developer.riotgames.com](https://developer.riotgames.com/)

## Installation Methods

### Method 1: Using UV (Recommended)

[UV](https://github.com/astral-sh/uv) is a fast Python package installer and resolver.

```bash
# Clone the repository
git clone https://github.com/OneStepAt4time/lolstonks-api-gateway.git
cd lolstonks-api-gateway

# Install the project with documentation dependencies
uv pip install -e ".[docs]"

# Activate the virtual environment
source .venv/bin/activate  # On Linux/macOS
# or
.venv\Scripts\activate     # On Windows
```

### Method 2: Using Pip

```bash
# Clone the repository
git clone https://github.com/OneStepAt4time/lolstonks-api-gateway.git
cd lolstonks-api-gateway

# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On Linux/macOS
# or
.venv\Scripts\activate     # On Windows

# Upgrade pip
pip install --upgrade pip

# Install the project in development mode
pip install -e ".[docs]"
```

### Method 3: Docker (Quick Start)

```bash
# Clone the repository
git clone https://github.com/OneStepAt4time/lolstonks-api-gateway.git
cd lolstonks-api-gateway

# Copy environment file
cp .env.example .env

# Edit .env with your Riot API key
# nano .env

# Start with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f
```

## Redis Setup

### Option 1: Docker (Recommended for Development)

```bash
# Start Redis with Docker
docker run -d --name redis -p 6379:6379 redis:7-alpine

# Or use Docker Compose (included in project)
docker-compose up -d redis
```

### Option 2: Local Installation

```bash
# On Ubuntu/Debian
sudo apt-get install redis-server

# On macOS with Homebrew
brew install redis

# On Windows
# Download and install Redis from https://redis.io/download
```

### Option 3: Redis Cloud

For production deployments, consider using managed Redis services:
- [Redis Cloud](https://redis.com/try-free/)
- [AWS ElastiCache](https://aws.amazon.com/elasticache/)
- [Azure Cache for Redis](https://azure.microsoft.com/en-us/products/cache/)

## Riot API Key Setup

1. Visit [Riot Developer Portal](https://developer.riotgames.com/)
2. Sign in with your Riot Games account
3. Create a new API key
4. Copy your API key (starts with `RGAPI-`)

## Environment Configuration

Create a `.env` file in the project root:

```env
# Required
RIOT_API_KEY=RGAPI-your-api-key-here

# Optional (defaults shown)
RIOT_DEFAULT_REGION=euw1
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
HOST=0.0.0.0
PORT=8080
LOG_LEVEL=INFO

# Rate limiting (requests per second)
RATE_LIMIT_RPS=20
RATE_LIMIT_BURST=100
```

## Verification

### Check Python Environment

```bash
python --version  # Should show Python 3.12+
pip list | grep fastapi  # Should show FastAPI installed
```

### Check Redis Connection

```bash
# Test Redis connection
redis-cli ping
# Should return: PONG
```

### Test Application

```bash
# Start the application
python -m app.main

# In another terminal, test health endpoint
curl http://localhost:8080/health
# Should return: {"status":"ok"}
```

## Troubleshooting

### Common Issues

1. **Python Version Error**
   ```bash
   # Error: Python 3.12+ required
   python --version  # Check your Python version
   # Install Python 3.12+ from python.org or pyenv
   ```

2. **Redis Connection Failed**
   ```bash
   # Check if Redis is running
   redis-cli ping

   # Check connection settings in .env
   # Ensure REDIS_HOST and REDIS_PORT are correct
   ```

3. **Import Errors**
   ```bash
   # Reinstall dependencies (using UV - recommended)
   uv pip install -e ".[docs]"
   # or using pip:
   pip install -e ".[docs]"

   # Check virtual environment activation
   which python  # Should point to your venv
   ```

4. **Permission Errors**
   ```bash
   # On Linux/macOS, check file permissions
   chmod +x scripts/*.py

   # On Windows, run as administrator if needed
   ```

### Getting Help

If you encounter issues during installation:

1. Check the [GitHub Issues](https://github.com/OneStepAt4time/lolstonks-api-gateway/issues)
2. Review the [Troubleshooting Guide](../development/testing.md#troubleshooting)
3. Create a new issue with:
   - Your operating system
   - Python version
   - Error messages
   - Steps to reproduce

## Next Steps

After successful installation:

1. Read the [Quick Start guide](quick-start.md)
2. Configure your [environment variables](configuration.md)
3. Explore the [API Reference](../api/overview.md)
4. Set up [development tools](../development/testing.md)