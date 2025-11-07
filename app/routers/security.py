"""
Security monitoring and configuration endpoints.

Provides security-related information including:
- Security configuration status
- Vulnerability scan results
- Rate limiting status
- Security headers validation
"""

from datetime import datetime
from typing import Dict

from fastapi import APIRouter
from loguru import logger

from app.config import settings
from app.providers.registry import get_registry

router = APIRouter(tags=["security"])


@router.get("/security/status")
async def security_status() -> Dict:
    """
    Get security configuration status for monitoring.

    Returns security assessment including:
    - Host configuration security
    - Rate limiting configuration
    - Provider authentication status
    - Redis connection security
    - API key rotation status

    Returns:
        Dict with security status information

    Example:
        >>> curl "http://127.0.0.1:8080/security/status"
    """
    logger.debug("Security status requested")

    # Check host configuration
    host_secure = settings.host == "127.0.0.1"

    # Check API key configuration
    try:
        api_keys = settings.get_api_keys()
        key_rotation_enabled = len(api_keys) > 1
        keys_configured = len(api_keys) > 0
    except Exception:
        keys_configured = False
        key_rotation_enabled = False

    # Check rate limiting
    rate_limiting_enabled = (
        settings.riot_rate_limit_per_second > 0 and settings.riot_rate_limit_per_2min > 0
    )

    # Check providers
    registry = get_registry()
    provider_count = len(registry.get_all_providers())

    # Overall security score
    security_issues = []

    if not host_secure:
        security_issues.append("Host not bound to localhost")

    if not keys_configured:
        security_issues.append("No API keys configured")

    if not rate_limiting_enabled:
        security_issues.append("Rate limiting disabled")

    security_score = max(0, 100 - (len(security_issues) * 25))

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "security_score": security_score,
        "security_status": "secure"
        if security_score >= 75
        else "at_risk"
        if security_score >= 50
        else "insecure",
        "checks": {
            "host_configuration": {
                "status": "secure" if host_secure else "insecure",
                "host": settings.host,
                "recommendation": "Use 127.0.0.1 for local access only"
                if not host_secure
                else None,
            },
            "api_keys": {
                "status": "configured" if keys_configured else "not_configured",
                "key_rotation_enabled": key_rotation_enabled,
                "key_count": len(api_keys) if keys_configured else 0,
                "recommendation": "Configure API keys in environment variables"
                if not keys_configured
                else None,
            },
            "rate_limiting": {
                "status": "enabled" if rate_limiting_enabled else "disabled",
                "per_second": settings.riot_rate_limit_per_second,
                "per_2min": settings.riot_rate_limit_per_2min,
                "recommendation": "Enable rate limiting to prevent API abuse"
                if not rate_limiting_enabled
                else None,
            },
            "providers": {
                "status": "active" if provider_count > 0 else "none",
                "count": provider_count,
                "recommendation": "Configure at least one data provider"
                if provider_count == 0
                else None,
            },
        },
        "security_issues": security_issues,
        "recommendations": [
            "Use environment variables for API keys",
            "Bind to localhost (127.0.0.1) in production",
            "Enable Redis authentication in production",
            "Monitor error rates for anomaly detection",
            "Regular security audits of dependencies",
        ],
    }


@router.get("/security/headers")
async def security_headers() -> Dict:
    """
    Get recommended security headers for the gateway.

    Returns security headers configuration:
    - CORS headers
    - Rate limiting headers
    - Security-related headers
    - CSP and other protection headers

    Returns:
        Dict with security header recommendations

    Example:
        >>> curl "http://127.0.0.1:8080/security/headers"
    """
    logger.debug("Security headers requested")

    return {
        "recommended_headers": {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
        },
        "rate_limiting_headers": {
            "X-RateLimit-Limit": f"{settings.riot_rate_limit_per_second},100;w=120",
            "X-RateLimit-Remaining": "dynamic",
            "X-RateLimit-Reset": "dynamic",
        },
        "cors_headers": {
            "Access-Control-Allow-Origin": "configured-per-origin",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Max-Age": "86400",
        },
    }


@router.get("/health/security")
async def security_health_check() -> Dict:
    """
    Simple security health check for monitoring systems.

    Returns basic security status:
    - Security configuration
    - Authentication status
    - Rate limiting status

    Returns:
        Dict with security health information

    Example:
        >>> curl "http://127.0.0.1:8080/health/security"
    """
    try:
        api_keys = settings.get_api_keys()
        keys_ok = len(api_keys) > 0
    except Exception:
        keys_ok = False

    host_ok = settings.host == "127.0.0.1"
    rate_limits_ok = (
        settings.riot_rate_limit_per_second > 0 and settings.riot_rate_limit_per_2min > 0
    )

    overall_status = "healthy" if all([keys_ok, host_ok, rate_limits_ok]) else "unhealthy"

    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            "api_keys": "ok" if keys_ok else "fail",
            "host_binding": "ok" if host_ok else "fail",
            "rate_limiting": "ok" if rate_limits_ok else "fail",
        },
    }
