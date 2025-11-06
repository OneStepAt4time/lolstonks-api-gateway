# Security API

The LOLStonks API Gateway includes comprehensive security monitoring and endpoint validation to ensure safe and secure operation.

## Security Endpoints

### Security Status Overview

**Endpoint**: `GET /security/status`

Returns overall security status and configuration validation.

**Response Example**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "host_binding": "secure",
  "api_keys_configured": true,
  "api_key_rotation_enabled": true,
  "input_validation_enabled": true,
  "rate_limiting_enabled": true,
  "security_headers": {
    "host_header": "configured",
    "cors_policy": "restrictive",
    "https_redirect": "not_applicable"
  }
}
```

### Security Headers Validation

**Endpoint**: `GET /security/headers`

Validates security headers and CORS configuration.

**Response Example**:
```json
{
  "status": "validated",
  "timestamp": "2024-01-01T12:00:00Z",
  "headers": {
    "host": "valid",
    "origin": "restrictive",
    "methods": "safe_methods_only",
    "credentials": "not_allowed"
  },
  "cors_policy": {
    "allowed_origins": [],
    "allowed_methods": ["GET", "OPTIONS"],
    "allowed_headers": ["Content-Type", "Authorization"],
    "max_age": 86400,
    "supports_credentials": false
  }
}
```

### Security Health Check

**Endpoint**: `GET /health/security`

Health check specifically for security monitoring components.

**Response Example**:
```json
{
  "status": "ok",
  "security_monitoring": "active",
  "error_tracking": "enabled",
  "alert_threshold": 10,
  "consecutive_errors": 0,
  "last_security_check": "2024-01-01T12:00:00Z"
}
```

## Security Features

### 1. Host Binding Security

**Configuration**: Gateway is bound to `127.0.0.1` by default for security.

**Purpose**: Prevents external access and reduces attack surface.

**Verification**:
```bash
# Check if properly secured
curl http://127.0.0.1:8080/security/status

# This will fail (intentionally)
curl http://0.0.0.0:8080/security/status
# Connection refused
```

**Override (Development Only)**:
```bash
# WARNING: Only use in trusted environments
HOST=0.0.0.0 uvicorn app.main:app
```

### 2. API Key Rotation

**Feature**: Automatic rotation across multiple API keys.

**Benefits**:
- Distributes load across multiple keys
- Prevents single key exhaustion
- Continues operation during rate limit events

**Configuration**:
```bash
# Multiple keys for rotation (recommended)
RIOT_API_KEYS=key1,key2,key3

# Single key (backward compatible)
RIOT_API_KEY=RGAPI-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

**Rotation Strategy**:
- Round-robin distribution
- Immediate fallback on 429 errors
- Health tracking per key
- Automatic key recovery

### 3. Input Validation

**Coverage**: Complete Pydantic model validation for all endpoints.

**Features**:
- Type safety for all parameters
- Regex validation for IDs and strings
- Range validation for numeric values
- Enum validation for constants
- Sanitization of user input

**Example Validation**:
```python
# Path parameter validation
@router.get("/summoner/by-name/{summoner_name}")
async def get_summoner_by_name(
    summoner_name: str = Path(..., min_length=3, max_length=16, pattern=r"^[0-9\\p{L} _]+$"),
    region: str = Query(..., enum=SUPPORTED_REGIONS)
):
    # summoner_name is validated before execution
```

### 4. Rate Limiting

**Algorithm**: Token bucket with configurable limits.

**Features**:
- Per-provider rate limiting
- Smooth request distribution
- Automatic retry with backoff
- Smart key rotation

**Configuration**:
```bash
# Riot API rate limits
RIOT_RATE_LIMIT_PER_SECOND=20
RIOT_RATE_LIMIT_PER_2MIN=100

# Custom provider limits
CUSTOM_PROVIDER_RATE_LIMIT=50
```

### 5. Error Monitoring

**Real-time Tracking**:
- Error counts and rates
- Consecutive failure tracking
- Error pattern detection
- Automatic alerting

**Alerting Thresholds**:
```bash
# Trigger alerts after N errors in window
ERROR_ALERT_THRESHOLD=10
ERROR_WINDOW_SIZE=300  # 5 minutes
```

**Error Types Monitored**:
- HTTP client errors (4xx, 5xx)
- Connection timeouts
- Data validation errors
- Provider-specific errors
- Security violations

## Security Best Practices

### API Key Management

1. **Never commit API keys** to version control
2. **Use environment variables** for all sensitive data
3. **Rotate keys regularly** for production systems
4. **Monitor key usage** and set up alerts

### Network Security

1. **Keep host binding** to `127.0.0.1` for local development
2. **Use reverse proxy** (nginx) for production deployment
3. **Implement HTTPS** in production environments
4. **Configure firewalls** to restrict access

### Input Validation

1. **Always validate** user input at API boundaries
2. **Use parameterized queries** to prevent injection
3. **Sanitize and escape** output data
4. **Implement rate limiting** per user/IP

### Monitoring & Logging

1. **Log security events** with timestamps
2. **Monitor error rates** and set up alerts
3. **Track API usage** patterns
4. **Regular security audits** of logs and configurations

## Security Headers

### Default Headers

```http
Content-Security-Policy: default-src 'self'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
```

### CORS Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[],  # Restrictive by default
    allow_credentials=False,
    allow_methods=["GET", "OPTIONS"],  # Safe methods only
    allow_headers=["Content-Type", "Authorization"],
    max_age=86400,
)
```

## Security Monitoring

### Real-time Metrics

- **Request Rate**: Requests per second by provider
- **Error Rate**: Percentage of failed requests
- **Response Time**: Average response time tracking
- **Concurrent Failures**: Count of consecutive errors

### Alert Conditions

- **High Error Rate**: >10% error rate sustained
- **Consecutive Failures**: 5+ failures in a row
- **Security Violations**: Invalid host headers, CORS violations
- **Rate Limit Breaches**: Exceeding configured limits

### Health Check Integration

Security status is integrated with overall health monitoring:

```bash
# Basic health includes security
curl http://localhost:8080/health

# Detailed security status
curl http://localhost:8080/security/status

# Security-specific health
curl http://localhost:8080/health/security
```

## Troubleshooting Security Issues

### Host Binding Issues

**Problem**: External access attempts fail

**Solution**: Check host configuration
```bash
# Should be 127.0.0.1 for security
echo $HOST

# Test local access
curl http://127.0.0.1:8080/health

# Test external access (should fail)
curl http://0.0.0.0:8080/health
```

### API Key Issues

**Problem**: 401 Unauthorized or 429 Rate Limited

**Solution**: Verify API key configuration
```bash
# Check key format
echo $RIOT_API_KEY | head -c 10

# Test API directly
curl -H "X-Riot-Token: $RIOT_API_KEY" \
     "https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/test"

# Check key rotation
curl http://localhost:8080/security/status | jq '.api_key_rotation_enabled'
```

### Input Validation Issues

**Problem**: 422 Unprocessable Entity errors

**Solution**: Check request parameters
```bash
# Check validation rules
curl http://localhost:8080/docs

# Test with valid parameters
curl "http://localhost:8080/lol/summoner/v4/summoners/by-name/ValidName?region=euw1"
```

### CORS Issues

**Problem**: Cross-origin requests blocked

**Solution**: Configure CORS properly
```bash
# Check CORS headers
curl -H "Origin: https://example.com" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS \
     "http://localhost:8080/summoner/by-name/test"

# Should return restrictive CORS headers
```

## Security Configuration Reference

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `127.0.0.1` | Server host binding |
| `RIOT_API_KEY` | None | Single API key (backward compatible) |
| `RIOT_API_KEYS` | None | Multiple API keys for rotation |
| `RIOT_RATE_LIMIT_PER_SECOND` | `20` | Rate limit per second |
| `RIOT_RATE_LIMIT_PER_2MIN` | `100` | Rate limit per 2 minutes |
| `ERROR_ALERT_THRESHOLD` | `10` | Error alerting threshold |
| `ENABLE_CORS` | `false` | Enable CORS middleware |

### Security Headers

| Header | Value | Purpose |
|--------|--------|---------|
| `X-Content-Type-Options` | `nosniff` | Prevent MIME type sniffing |
| `X-Frame-Options` | `DENY` | Prevent clickjacking |
| `X-XSS-Protection` | `1; mode=block` | Enable XSS protection |
| `Content-Security-Policy` | `default-src 'self'` | Content security policy |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Referrer policy |
