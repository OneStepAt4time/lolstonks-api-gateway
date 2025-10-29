# Security Best Practices

This guide covers security considerations and best practices for deploying and operating the LOLStonks API Gateway in production environments.

> **📝 Documentation Note**: This document describes **security best practices and potential implementations**. Many advanced security features represent future enhancements rather than current implementation.
>
> **Currently Implemented** ✅:
> - Input validation using Pydantic models
> - Basic rate limiting (Riot API level with aiolimiter)
> - API key loading from environment variables
> - Redis password authentication (if configured)
>
> **Not Yet Implemented** ❌ (Potential Future Enhancements):
> - API key rotation system
> - IP-based rate limiting and blocking
> - Advanced input sanitization
> - CORS middleware
> - HTTPS redirect middleware
> - Security event logging
> - Prometheus security metrics
>
> For actual implementation details, see [Implementation Details](../architecture/implementation-details.md).

## Overview

Security is implemented through multiple layers of protection:

1. **Input Validation**: Comprehensive request validation using Pydantic models ✅
2. **Rate Limiting**: Protection against abuse and DoS attacks ⚠️ (Riot API level only)
3. **Authentication & Authorization**: Secure API key management ⚠️ (Basic environment variable)
4. **Network Security**: Firewall rules and secure communications ⚠️ (Infrastructure level)
5. **Monitoring & Auditing**: Comprehensive logging and threat detection ❌ (Not implemented)

## API Key Security

### Secure Key Management

#### Environment-Based Configuration

```env
# Never hardcode API keys in source code
RIOT_API_KEY=RGAPI-your-secure-api-key

# Use separate keys for different environments
RIOT_API_KEY_DEV=RGAPI-dev-key
RIOT_API_KEY_STAGING=RGAPI-staging-key
RIOT_API_KEY_PROD=RGAPI-production-key
```

#### Current Implementation

```env
# .env file (ACTUAL IMPLEMENTATION)
RIOT_API_KEY=RGAPI-your-secure-api-key
```

The API key is loaded from environment variables using Pydantic Settings:

```python
# app/config.py (ACTUAL IMPLEMENTATION)
class Settings(BaseSettings):
    riot_api_key: str  # Required from environment
```

#### Key Rotation Strategy (Potential Enhancement)

> **Not Implemented**: API key rotation is not currently automated. Keys must be rotated manually.

```python
# Example: app/security.py (NOT IMPLEMENTED)
import os
from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class APIKeyManager:
    """Manages Riot API key rotation and validation."""

    def __init__(self):
        self.current_key = os.getenv("RIOT_API_KEY")
        self.backup_key = os.getenv("RIOT_API_KEY_BACKUP")
        self.last_rotation = datetime.now()
        self.rotation_interval = timedelta(days=20)  # Riot API keys last 30 days

    def get_active_key(self) -> str:
        """Get the currently active API key."""
        # Check if key needs rotation
        if datetime.now() - self.last_rotation > self.rotation_interval:
            logger.warning("API key rotation recommended")

        return self.current_key

    def validate_key_format(self, key: str) -> bool:
        """Validate API key format."""
        import re
        pattern = r'^RGAPI-[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$'
        return bool(re.match(pattern, key))
```

#### Key Storage Best Practices

1. **Use Environment Variables**: Never store keys in code or configuration files
2. **Separate Environments**: Use different keys for dev, staging, and production
3. **Regular Rotation**: Rotate keys every 20-25 days (Riot API keys expire in 30 days)
4. **Backup Keys**: Maintain backup keys for failover scenarios
5. **Access Control**: Limit access to API keys to only necessary personnel

## Input Validation & Sanitization

### Pydantic Model Validation (Currently Implemented ✅)

All API inputs are validated using Pydantic models. This is **currently implemented** in the codebase:

```python
# app/models/security.py
from pydantic import BaseModel, Field, validator
import re
from typing import Optional

class SecureSummonerNameParams(BaseModel):
    """Securely validated summoner name parameters."""

    summonerName: str = Field(
        min_length=1,
        max_length=16,
        description="Summoner name (1-16 characters)"
    )

    @validator('summonerName')
    def validate_summoner_name(cls, v):
        """Validate summoner name format."""
        # Remove potentially dangerous characters
        cleaned = re.sub(r'[^\w\s]', '', v.strip())

        # Check for allowed characters (letters, numbers, spaces)
        if not re.match(r'^[a-zA-Z0-9\s]+$', cleaned):
            raise ValueError('Invalid summoner name format')

        return cleaned

class SecureRegionQuery(BaseModel):
    """Securely validated region parameters."""

    region: str = Field(
        default="euw1",
        description="Riot API region code"
    )

    @validator('region')
    def validate_region(cls, v):
        """Validate region code against allowed list."""
        allowed_regions = {
            'euw1', 'eun1', 'tr1', 'ru',  # Europe
            'na1', 'br1', 'la1', 'la2',   # Americas
            'kr', 'jp1',                  # Asia
            'oc1', 'ph2', 'sg2', 'th2', 'tw2', 'vn2'  # SEA/Oceania
        }

        if v.lower() not in allowed_regions:
            raise ValueError(f'Invalid region: {v}')

        return v.lower()
```

### Advanced Input Sanitization (Potential Enhancement)

> **Not Implemented**: Advanced input sanitization beyond Pydantic validation is not currently implemented.

The current implementation relies on Pydantic validators (shown above). More advanced sanitization could be added:

```python
# Example: app/security/validation.py (NOT IMPLEMENTED)
import re
from typing import Any, Dict, List

class SecurityValidator:
    """Security-focused input validation."""

    @staticmethod
    def sanitize_string(input_str: str, max_length: int = 100) -> str:
        """Sanitize string inputs."""
        if not isinstance(input_str, str):
            raise TypeError("Input must be a string")

        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\';\\&]', '', input_str)

        # Truncate to max length
        sanitized = sanitized[:max_length]

        return sanitized.strip()

    @staticmethod
    def validate_puuid(puuid: str) -> bool:
        """Validate PUUID format."""
        pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        return bool(re.match(pattern, puuid.lower()))

    @staticmethod
    def validate_match_id(match_id: str) -> bool:
        """Validate match ID format."""
        pattern = r'^[A-Z0-9_]+$'
        return bool(re.match(pattern, match_id))
```

## Rate Limiting & DDoS Protection

### Current Implementation

The application implements rate limiting **only at the Riot API level** using aiolimiter:

```python
# app/riot/rate_limiter.py (ACTUAL IMPLEMENTATION)
from aiolimiter import AsyncLimiter

class RiotRateLimiter:
    def __init__(self):
        self.limiter_1s = AsyncLimiter(
            max_rate=settings.riot_rate_limit_per_second,
            time_period=1,
        )
        self.limiter_2min = AsyncLimiter(
            max_rate=settings.riot_rate_limit_per_2min,
            time_period=120,
        )
```

> **Limitation**: This only limits requests to the Riot API, not incoming requests from clients.

### IP-Based Rate Limiting (Potential Enhancement)

> **Not Implemented**: Per-IP rate limiting and DDoS protection are not currently implemented.

```python
# Example: app/security/rate_limiting.py (NOT IMPLEMENTED)
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException
import redis
import json

# Initialize rate limiter with Redis backend
redis_client = redis.Redis(
    host='localhost',
    port=6379,
    password='your-redis-password',
    decode_responses=True
)

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379",
    default_limits=["1000/hour"]  # Global limit
)

# Custom rate limit exceeded handler
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom handler for rate limit exceeded."""
    client_ip = get_remote_address(request)
    logger.warning(f"Rate limit exceeded for IP: {client_ip}")

    raise HTTPException(
        status_code=429,
        detail={
            "error": "Rate limit exceeded",
            "message": "Too many requests. Please try again later.",
            "retry_after": exc.detail  # Seconds to wait
        }
    )

# Apply rate limiting to sensitive endpoints
@app.get("/summoner/by-name/{summonerName}")
@limiter.limit("100/minute")  # Stricter limit for summoner lookups
async def get_summoner_by_name(
    request: Request,
    summonerName: str,
    region: str = "euw1"
):
    """Get summoner by name with rate limiting."""
    pass
```

### IP-Based Blocking (Potential Enhancement)

> **Not Implemented**: IP blocking is not currently implemented.

```python
# Example: app/security/ip_blocking.py (NOT IMPLEMENTED)
from typing import Set, Dict
from datetime import datetime, timedelta
import json

class IPBlocker:
    """Manages IP blocking for malicious actors."""

    def __init__(self, redis_client):
        self.redis = redis_client
        self.block_duration = timedelta(hours=1)
        self.permanent_block_threshold = 100  # Violations for permanent block

    async def block_ip(self, ip: str, reason: str, permanent: bool = False):
        """Block an IP address."""
        block_data = {
            "ip": ip,
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
            "permanent": permanent
        }

        if permanent:
            await self.redis.set(f"blocked_ip:{ip}", json.dumps(block_data))
        else:
            await self.redis.setex(
                f"blocked_ip:{ip}",
                int(self.block_duration.total_seconds()),
                json.dumps(block_data)
            )

    async def is_ip_blocked(self, ip: str) -> bool:
        """Check if IP is blocked."""
        return await self.redis.exists(f"blocked_ip:{ip}")

    async def record_violation(self, ip: str, violation_type: str):
        """Record a security violation."""
        violation_key = f"violations:{ip}"

        # Increment violation count
        count = await self.redis.incr(violation_key)
        await self.redis.expire(violation_key, 86400)  # 24 hours

        # Check if should be permanently blocked
        if count >= self.permanent_block_threshold:
            await self.block_ip(ip, f"Too many violations: {count}", permanent=True)

        return count

# Middleware for IP blocking
@app.middleware("http")
async def ip_blocking_middleware(request: Request, call_next):
    """Check for blocked IPs before processing requests."""
    client_ip = get_remote_address(request)

    if await ip_blocker.is_ip_blocked(client_ip):
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    response = await call_next(request)
    return response
```

## Network Security

> **Infrastructure Level**: Network security is typically handled at the infrastructure/deployment level, not in application code.

### SSL/TLS Configuration

#### Nginx SSL Configuration (Deployment Best Practice ✅)

```nginx
# /etc/nginx/sites-available/lolstonks-api
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    # Strong SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'"; always;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # SSL offloading
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header X-Forwarded-SSL on;
    }
}
```

#### Application SSL Settings (Potential Enhancement)

> **Not Implemented**: HTTPS redirect and trusted host middleware are not currently configured in the application.

```python
# Example: app/security/ssl.py (NOT IMPLEMENTED)
from fastapi import FastAPI
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

def configure_security_middleware(app: FastAPI):
    """Configure security middleware for the FastAPI app."""

    # Force HTTPS in production
    if os.getenv("ENVIRONMENT") == "production":
        app.add_middleware(HTTPSRedirectMiddleware)

    # Only allow trusted hosts
    allowed_hosts = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=allowed_hosts
    )

    return app
```

### Firewall Configuration (Deployment Best Practice ✅)

> **Infrastructure Level**: Firewall configuration is handled at the system/deployment level.

```bash
#!/bin/bash
# Example: firewall_setup.sh

# Reset firewall rules
sudo ufw --force reset

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH (restrict to your IP if possible)
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow Redis only from localhost
sudo ufw allow from 127.0.0.1 to any port 6379

# Rate limiting for HTTP
sudo ufw limit 80/tcp
sudo ufw limit 443/tcp

# Enable firewall
sudo ufw --force enable

# Show status
sudo ufw status verbose
```

## Authentication & Authorization

> **Not Implemented**: Advanced authentication for admin endpoints is not currently implemented.

The current implementation only uses the Riot API key for accessing Riot's services. There is no authentication for accessing the gateway itself.

### API Key Authentication (Potential Enhancement)

> **Not Implemented**: API key authentication for gateway endpoints is not currently implemented.

```python
# Example: app/security/auth.py (NOT IMPLEMENTED)
from fastapi import HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
import os
import hashlib
import hmac

class APIKeyAuth:
    """API key authentication for admin endpoints."""

    def __init__(self):
        self.api_key = os.getenv("ADMIN_API_KEY")
        if not self.api_key:
            raise ValueError("ADMIN_API_KEY environment variable required")

    def verify_key(self, provided_key: str) -> bool:
        """Verify provided API key using constant-time comparison."""
        return hmac.compare_digest(
            hashlib.sha256(provided_key.encode()).hexdigest(),
            hashlib.sha256(self.api_key.encode()).hexdigest()
        )

# Initialize API key authentication
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
auth = APIKeyAuth()

async def verify_api_key(api_key: str = Security(api_key_header)):
    """Dependency for API key verification."""
    if not api_key or not auth.verify_key(api_key):
        raise HTTPException(
            status_code=403,
            detail="Invalid or missing API key"
        )
    return api_key

# Usage in endpoints
@app.get("/admin/stats")
async def get_admin_stats(api_key: str = Depends(verify_api_key)):
    """Admin-only endpoint with API key authentication."""
    pass
```

### CORS Configuration (Potential Enhancement)

> **Not Implemented**: CORS middleware is not currently configured.

```python
# Example: app/security/cors.py (NOT IMPLEMENTED)
from fastapi.middleware.cors import CORSMiddleware
import os

def configure_cors(app: FastAPI):
    """Configure CORS based on environment."""

    # Production CORS settings
    if os.getenv("ENVIRONMENT") == "production":
        allowed_origins = os.getenv("CORS_ORIGINS", "https://yourdomain.com").split(",")
        app.add_middleware(
            CORSMiddleware,
            allow_origins=allowed_origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE"],
            allow_headers=["*"],
            expose_headers=["X-Request-ID"]
        )
    else:
        # Development CORS settings
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"]
        )
```

## Logging & Monitoring

### Current Implementation

The application uses basic Loguru logging (see monitoring.md). Security-specific logging is not currently implemented.

### Security Logging (Potential Enhancement)

> **Not Implemented**: Dedicated security event logging is not currently implemented.

```python
# Example: app/security/logging.py (NOT IMPLEMENTED)
import logging
import json
from datetime import datetime
from typing import Dict, Any

class SecurityLogger:
    """Specialized logger for security events."""

    def __init__(self):
        self.logger = logging.getLogger("security")

        # Configure security logger
        handler = logging.FileHandler("/var/log/lolstonks/security.log")
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log a security event."""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "details": details
        }

        self.logger.info(json.dumps(event))

    def log_blocked_request(self, ip: str, endpoint: str, reason: str):
        """Log a blocked request."""
        self.log_security_event("blocked_request", {
            "ip": ip,
            "endpoint": endpoint,
            "reason": reason
        })

    def log_rate_limit_violation(self, ip: str, endpoint: str):
        """Log rate limit violation."""
        self.log_security_event("rate_limit_violation", {
            "ip": ip,
            "endpoint": endpoint
        })

    def log_authentication_failure(self, ip: str, key_provided: bool):
        """Log authentication failure."""
        self.log_security_event("auth_failure", {
            "ip": ip,
            "key_provided": key_provided
        })

# Initialize security logger
security_logger = SecurityLogger()
```

### Security Monitoring (Potential Enhancement)

> **Not Implemented**: Security metrics are not currently tracked.

```python
# Example: app/security/monitoring.py (NOT IMPLEMENTED)
from prometheus_client import Counter, Histogram
import time
import hashlib

# Security metrics
SECURITY_EVENTS = Counter(
    'lolstonks_security_events_total',
    'Total security events',
    ['event_type', 'severity']
)

AUTHENTICATION_ATTEMPTS = Counter(
    'lolstonks_authentication_attempts_total',
    'Total authentication attempts',
    ['result']
)

RATE_LIMIT_VIOLATIONS = Counter(
    'lolstonks_rate_limit_violations_total',
    'Total rate limit violations',
    ['ip', 'endpoint']
)

class SecurityMonitor:
    """Security monitoring and alerting."""

    @staticmethod
    def track_security_event(event_type: str, severity: str = "medium"):
        """Track security events for metrics."""
        SECURITY_EVENTS.labels(event_type=event_type, severity=severity).inc()

    @staticmethod
    def track_authentication_attempt(success: bool, ip: str):
        """Track authentication attempts."""
        result = "success" if success else "failure"
        AUTHENTICATION_ATTEMPTS.labels(result=result).inc()

        # Log suspicious patterns
        if not success:
            SecurityMonitor.check_suspicious_ip(ip)

    @staticmethod
    def check_suspicious_ip(ip: str):
        """Check for suspicious IP patterns."""
        # Hash IP for privacy
        ip_hash = hashlib.sha256(ip.encode()).hexdigest()[:16]

        # In production, you might check against:
        # - Known malicious IP databases
        # - Geographic anomalies
        # - Unusual request patterns
        pass
```

## Security Auditing

### Regular Security Checks (Best Practice ✅)

> **Recommended Practice**: These scripts are examples for manual or automated security audits.

```bash
#!/bin/bash
# Example: security_audit.sh

echo "=== LOLStonks Security Audit ==="
echo "Date: $(date)"
echo

# Check for exposed API keys
echo "1. Checking for exposed API keys..."
if grep -r "RGAPI-" /home/lolstonks/lolstonks-api-gateway/ --exclude-dir=.git; then
    echo "⚠️  WARNING: Potential exposed API keys found!"
else
    echo "✅ No exposed API keys found"
fi

# Check file permissions
echo -e "\n2. Checking file permissions..."
find /home/lolstonks/lolstonks-api-gateway/ -type f -name "*.env" -exec ls -la {} \;

# Check SSL certificate expiry
echo -e "\n3. Checking SSL certificate..."
if command -v certbot >/dev/null 2>&1; then
    certbot certificates
else
    echo "Certbot not installed"
fi

# Check firewall status
echo -e "\n4. Checking firewall status..."
sudo ufw status

# Check running services
echo -e "\n5. Checking running services..."
systemctl list-units --type=service --state=running | grep -E "(nginx|redis|lolstonks)"

# Check log for suspicious activity
echo -e "\n6. Recent security events..."
if [ -f /var/log/lolstonks/security.log ]; then
    tail -20 /var/log/lolstonks/security.log
else
    echo "Security log not found"
fi

echo -e "\n=== Audit Complete ==="
```

### Security Checklist

- [ ] **API Key Management**
  - [ ] API keys stored in environment variables only
  - [ ] Regular key rotation (every 20-25 days)
  - [ ] Separate keys for different environments
  - [ ] Backup keys available for failover

- [ ] **Input Validation**
  - [ ] All inputs validated using Pydantic models
  - [ ] String inputs sanitized and length-limited
  - [ ] Pattern validation for IDs and special formats
  - [ ] SQL injection prevention measures in place

- [ ] **Rate Limiting**
  - [ ] Global rate limits configured
  - [ ] Endpoint-specific rate limits for sensitive operations
  - [ ] IP-based blocking for abusive behavior
  - [ ] DDoS protection at multiple levels

- [ ] **Network Security**
  - [ ] HTTPS enforced in production
  - [ ] Strong SSL/TLS configuration
  - [ ] Security headers implemented
  - [ ] Firewall rules configured
  - [ ] CORS properly configured

- [ ] **Authentication**
  - [ ] Admin endpoints protected with API keys
  - [ ] Constant-time comparison for secrets
  - [ ] Secure session management
  - [ ] Proper logout mechanisms

- [ ] **Logging & Monitoring**
  - [ ] Security events logged separately
  - [ ] Failed authentication attempts tracked
  - [ ] Suspicious activity alerts configured
  - [ ] Log files properly secured and rotated

- [ ] **Regular Maintenance**
  - [ ] Security audits performed regularly
  - [ ] Dependencies kept up to date
  - [ ] SSL certificates monitored for expiry
  - [ ] Backup and recovery procedures tested

---

## Summary

This document outlines **security best practices and potential implementations** for production deployments.

**Current Security Measures** ✅:
- Pydantic input validation on all endpoints
- Riot API rate limiting (prevents excessive API usage)
- Environment-based API key management
- Basic logging with Loguru

**Recommended Infrastructure Security** (handled at deployment level):
- Firewall configuration (ufw/iptables)
- SSL/TLS termination (Nginx)
- System-level hardening

**Future Security Enhancements** ❌ (Not Implemented):
- IP-based rate limiting and blocking
- CORS middleware
- Security event logging
- Prometheus security metrics
- API key rotation automation
- Admin endpoint authentication

For the actual implementation status, see [Implementation Status](implementation-status.md).
