# Monitoring and Observability

This guide covers monitoring, logging, and observability for the LOLStonks API Gateway in production environments.

> **📝 Documentation Note**: This document describes **best practices and potential implementations** for production monitoring. Many of these features represent future enhancements rather than current implementation.
>
> **Currently Implemented** ✅:
> - Basic health check endpoint (`/health` returns `{"status": "ok"}`)
> - Loguru logging to stderr
> - Basic application startup/shutdown logging
>
> **Not Yet Implemented** ❌ (Potential Future Enhancements):
> - Prometheus metrics collection
> - Grafana dashboards
> - ELK stack integration
> - OpenTelemetry distributed tracing
> - Advanced health checks (Redis/Riot API status)
> - Custom metrics middleware
>
> For actual implementation details, see [Implementation Details](../architecture/implementation-details.md).

## Overview

Effective monitoring ensures:
- **Proactive Issue Detection**: Identify problems before users notice
- **Performance Optimization**: Track and optimize system performance
- **Capacity Planning**: Understand resource usage and scaling needs
- **Security Monitoring**: Detect unusual activity and potential threats

## Core Monitoring Components

### 1. Application Metrics

#### Key Performance Indicators (KPIs)

| Metric | Description | Target | Alert Threshold |
|--------|-------------|---------|-----------------|
| Request Rate | API requests per second | Variable | > 1000 req/s |
| Response Time | Average API response time | < 200ms | > 500ms |
| Error Rate | Percentage of failed requests | < 1% | > 5% |
| Cache Hit Rate | Percentage of requests served from cache | > 80% | < 60% |
| Memory Usage | Application memory consumption | < 2GB | > 3GB |
| CPU Usage | Application CPU utilization | < 70% | > 85% |

#### Custom Metrics Implementation

> **💡 Potential Implementation**: The code below shows how to implement Prometheus metrics. This is **not currently implemented** in the codebase.

```python
# Example: app/monitoring.py (NOT IMPLEMENTED)
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import time
import logging

# Define metrics
REQUEST_COUNT = Counter(
    'lolstonks_requests_total',
    'Total number of API requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'lolstonks_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

CACHE_HIT_RATE = Gauge(
    'lolstonks_cache_hit_rate',
    'Cache hit rate percentage'
)

ACTIVE_CONNECTIONS = Gauge(
    'lolstonks_active_connections',
    'Number of active connections'
)

class MetricsMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            start_time = time.time()

            # Process request
            await self.app(scope, receive, send)

            # Record metrics
            duration = time.time() - start_time
            REQUEST_DURATION.labels(
                method=scope["method"],
                endpoint=scope["path"]
            ).observe(duration)

            REQUEST_COUNT.labels(
                method=scope["method"],
                endpoint=scope["path"],
                status="200"  # Would be set from actual response
            ).inc()
        else:
            await self.app(scope, receive, send)
```

### 2. Health Checks

#### Current Implementation

The actual health check endpoint is very simple:

```python
# app/routers/health.py (ACTUAL IMPLEMENTATION)
@router.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}
```

#### Comprehensive Health Endpoint (Potential Enhancement)

> **💡 Potential Implementation**: Below is an example of an advanced health check. This is **not currently implemented**.

```python
# Example: Comprehensive health check (NOT IMPLEMENTED)
from fastapi import APIRouter, Depends
from app.cache.redis_cache import RedisCache
from app.riot.client import RiotClient
import asyncio
import time

router = APIRouter()

@router.get("/health")
async def health_check():
    """Comprehensive health check endpoint."""
    start_time = time.time()

    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0",
        "checks": {},
        "duration_ms": 0
    }

    # Check Redis
    try:
        redis_health = await check_redis_health()
        health_status["checks"]["redis"] = redis_health
    except Exception as e:
        health_status["checks"]["redis"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"

    # Check Riot API connectivity
    try:
        riot_health = await check_riot_api_health()
        health_status["checks"]["riot_api"] = riot_health
    except Exception as e:
        health_status["checks"]["riot_api"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"

    # Check system resources
    try:
        system_health = check_system_health()
        health_status["checks"]["system"] = system_health
    except Exception as e:
        health_status["checks"]["system"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "unhealthy"

    health_status["duration_ms"] = int((time.time() - start_time) * 1000)

    return health_status

async def check_redis_health():
    """Check Redis connectivity and performance."""
    cache = RedisCache()

    # Test basic connectivity
    start_time = time.time()
    await cache.set("health_check", "ok", ttl=10)
    result = await cache.get("health_check")
    duration = time.time() - start_time

    if result != "ok":
        raise Exception("Redis read/write test failed")

    # Get Redis info
    import redis
    redis_client = redis.Redis(
        host=cache.redis_host,
        port=cache.redis_port,
        password=cache.redis_password,
        decode_responses=True
    )

    info = redis_client.info()

    return {
        "status": "healthy",
        "response_time_ms": int(duration * 1000),
        "memory_usage": info.get("used_memory_human"),
        "connected_clients": info.get("connected_clients"),
        "uptime_seconds": info.get("uptime_in_seconds")
    }

async def check_riot_api_health():
    """Check Riot API connectivity."""
    client = RiotClient()

    start_time = time.time()
    response = await client.get(
        "/lol/status/v4/platform-data",
        region="na1"
    )
    duration = time.time() - start_time

    if response.status_code != 200:
        raise Exception(f"Riot API returned status {response.status_code}")

    return {
        "status": "healthy",
        "response_time_ms": int(duration * 1000),
        "status_code": response.status_code
    }

def check_system_health():
    """Check system resources."""
    import psutil

    # CPU usage
    cpu_percent = psutil.cpu_percent(interval=1)

    # Memory usage
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    # Network connections
    connections = len(psutil.net_connections())

    system_health = {
        "status": "healthy",
        "cpu_percent": cpu_percent,
        "memory_percent": memory.percent,
        "memory_available_gb": round(memory.available / (1024**3), 2),
        "disk_percent": disk.percent,
        "disk_free_gb": round(disk.free / (1024**3), 2),
        "network_connections": connections
    }

    # Determine overall status
    if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
        system_health["status"] = "critical"
    elif cpu_percent > 80 or memory.percent > 80 or disk.percent > 80:
        system_health["status"] = "warning"

    return system_health
```

### 3. Logging Strategy

#### Current Implementation

The application uses Loguru for logging:

```python
# app/main.py (ACTUAL IMPLEMENTATION)
from loguru import logger

logger.remove()  # Remove default handler
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=settings.log_level,
    colorize=True,
)
```

#### Structured Logging Configuration (Potential Enhancement)

> **💡 Potential Implementation**: Below is an example of JSON structured logging. This is **not currently implemented**.

```python
# Example: app/logging_config.py (NOT IMPLEMENTED)
import logging
import json
import sys
from datetime import datetime
from pathlib import Path

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno',
                          'pathname', 'filename', 'module', 'exc_info',
                          'exc_text', 'stack_info', 'lineno', 'funcName',
                          'created', 'msecs', 'relativeCreated', 'thread',
                          'threadName', 'processName', 'process', 'message']:
                log_entry[key] = value

        return json.dumps(log_entry)

def setup_logging():
    """Configure structured logging for the application."""

    # Create logs directory
    log_dir = Path("/var/log/lolstonks")
    log_dir.mkdir(exist_ok=True)

    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_dir / "api.log")
        ]
    )

    # Set JSON formatter for all handlers
    for handler in logging.root.handlers:
        handler.setFormatter(JSONFormatter())

    # Configure specific loggers
    loggers = [
        "uvicorn.access",
        "uvicorn.error",
        "app.riot.client",
        "app.cache.redis_cache"
    ]

    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)
```

#### Request Logging Middleware

```python
# app/middleware.py
import time
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Generate unique request ID
        request_id = str(uuid.uuid4())

        # Log request start
        start_time = time.time()

        logger = logging.getLogger("request")
        logger.info(
            "Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "client_ip": request.client.host,
                "user_agent": request.headers.get("user-agent")
            }
        )

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Log request completion
            logger.info(
                "Request completed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "url": str(request.url),
                    "status_code": response.status_code,
                    "duration_ms": int(duration * 1000),
                    "response_size": response.headers.get("content-length", 0)
                }
            )

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            # Log request error
            duration = time.time() - start_time
            logger.error(
                "Request failed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "url": str(request.url),
                    "duration_ms": int(duration * 1000),
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            raise
```

## Monitoring Setup

> **💡 Section Note**: The monitoring tools described below (Prometheus, Grafana, ELK, OpenTelemetry) are **not currently implemented**. These are best practices and examples for potential future implementation.

### Prometheus Configuration

> **Not Implemented**: Prometheus is not currently set up for this project.

#### prometheus.yml (Example Configuration)

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'lolstonks-api'
    static_configs:
      - targets: ['localhost:9090']
    metrics_path: '/metrics'
    scrape_interval: 5s
    scrape_timeout: 5s

  - job_name: 'redis'
    static_configs:
      - targets: ['localhost:9121']

  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']
```

#### Alert Rules

```yaml
# alert_rules.yml
groups:
  - name: lolstonks_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(lolstonks_requests_total{status!~"2.."}[5m]) / rate(lolstonks_requests_total[5m]) > 0.05
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }} for the last 5 minutes"

      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(lolstonks_request_duration_seconds_bucket[5m])) > 0.5
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High response time detected"
          description: "95th percentile response time is {{ $value }}s"

      - alert: LowCacheHitRate
        expr: lolstonks_cache_hit_rate < 0.6
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Low cache hit rate"
          description: "Cache hit rate is {{ $value | humanizePercentage }}"

      - alert: HighMemoryUsage
        expr: process_resident_memory_bytes / 1024 / 1024 > 3000
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High memory usage"
          description: "Memory usage is {{ $value }}MB"

      - alert: ServiceDown
        expr: up{job="lolstonks-api"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service is down"
          description: "LOLStonks API Gateway has been down for more than 1 minute"
```

### Grafana Dashboard

> **Not Implemented**: Grafana dashboards are not currently configured.

#### Dashboard Configuration (Example)

```json
{
  "dashboard": {
    "id": null,
    "title": "LOLStonks API Gateway",
    "tags": ["lolstonks", "api"],
    "timezone": "browser",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(lolstonks_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ],
        "yAxes": [
          {
            "label": "Requests/sec"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(lolstonks_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          },
          {
            "expr": "histogram_quantile(0.50, rate(lolstonks_request_duration_seconds_bucket[5m]))",
            "legendFormat": "50th percentile"
          }
        ],
        "yAxes": [
          {
            "label": "Seconds"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(lolstonks_requests_total{status!~\"2..\"}[5m]) / rate(lolstonks_requests_total[5m])",
            "legendFormat": "Error Rate"
          }
        ],
        "yAxes": [
          {
            "label": "Percentage",
            "max": 1,
            "min": 0
          }
        ]
      },
      {
        "title": "Cache Hit Rate",
        "type": "singlestat",
        "targets": [
          {
            "expr": "lolstonks_cache_hit_rate",
            "legendFormat": "Cache Hit Rate"
          }
        ],
        "valueMaps": [
          {
            "value": "null",
            "text": "N/A"
          }
        ],
        "thresholds": "0.6,0.8"
      },
      {
        "title": "Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "process_resident_memory_bytes / 1024 / 1024",
            "legendFormat": "Memory (MB)"
          }
        ],
        "yAxes": [
          {
            "label": "MB"
          }
        ]
      },
      {
        "title": "CPU Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(process_cpu_seconds_total[5m]) * 100",
            "legendFormat": "CPU %"
          }
        ],
        "yAxes": [
          {
            "label": "Percentage",
            "max": 100,
            "min": 0
          }
        ]
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "5s"
  }
}
```

## Log Management

> **Not Implemented**: ELK Stack (Elasticsearch, Logstash, Kibana) is not currently configured.

### Log Aggregation with ELK Stack (Example)

#### Logstash Configuration (Example)

```ruby
# logstash.conf
input {
  file {
    path => "/var/log/lolstonks/api.log"
    start_position => "beginning"
    codec => json
  }
}

filter {
  # Parse timestamp
  date {
    match => [ "timestamp", "ISO8601" ]
  }

  # Add fields
  mutate {
    add_field => { "service" => "lolstonks-api" }
    add_field => { "environment" => "production" }
  }

  # Parse request logs
  if [request_id] {
    mutate {
      add_field => { "log_type" => "request" }
    }
  }

  # Parse error logs
  if [level] == "ERROR" or [level] == "CRITICAL" {
    mutate {
      add_field => { "log_type" => "error" }
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "lolstonks-logs-%{+YYYY.MM.dd}"
  }

  # Also output to stdout for debugging
  stdout {
    codec => rubydebug
  }
}
```

#### Kibana Dashboard Configuration

```javascript
// Kibana saved objects for LOLStonks monitoring
{
  "dashboard": {
    "title": "LOLStonks Logs",
    "panels": [
      {
        "title": "Request Rate Over Time",
        "type": "histogram",
        "query": "log_type:request",
        "timeField": "@timestamp"
      },
      {
        "title": "Error Distribution",
        "type": "pie",
        "query": "level:ERROR OR level:CRITICAL",
        "field": "error_type"
      },
      {
        "title": "Response Time Distribution",
        "type": "histogram",
        "query": "duration_ms:*",
        "field": "duration_ms"
      },
      {
        "title": "Recent Errors",
        "type": "table",
        "query": "level:ERROR OR level:CRITICAL",
        "sort": ["@timestamp", "desc"],
        "columns": ["@timestamp", "message", "request_id", "endpoint"]
      }
    ]
  }
}
```

## Advanced Monitoring

> **Not Implemented**: The advanced monitoring features below are not currently implemented.

### Distributed Tracing with OpenTelemetry (Potential Enhancement)

> **Not Implemented**: OpenTelemetry tracing is not currently configured.

```python
# Example: app/tracing.py (NOT IMPLEMENTED)
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor

def setup_tracing():
    """Configure OpenTelemetry tracing."""

    # Set up tracer
    trace.set_tracer_provider(TracerProvider())
    tracer = trace.get_tracer(__name__)

    # Configure Jaeger exporter
    jaeger_exporter = JaegerExporter(
        agent_host_name="localhost",
        agent_port=6831,
    )

    # Add span processor
    span_processor = BatchSpanProcessor(jaeger_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)

    # Instrument FastAPI
    FastAPIInstrumentor.instrument()

    # Instrument HTTP clients
    HTTPXClientInstrumentor.instrument()

    # Instrument Redis
    RedisInstrumentor.instrument()
```

### Custom Metrics (Potential Enhancement)

> **Not Implemented**: Custom business metrics are not currently tracked.

```python
# Example: app/custom_metrics.py (NOT IMPLEMENTED)
from prometheus_client import Counter, Histogram, Gauge
import time
import functools

# Business metrics
SUMMONER_LOOKUPS = Counter(
    'lolstonks_summoner_lookups_total',
    'Total number of summoner lookups',
    ['region', 'source_type']
)

MATCH_LOOKUPS = Counter(
    'lolstonks_match_lookups_total',
    'Total number of match lookups',
    ['region', 'queue_type']
)

API_KEY_USAGE = Counter(
    'lolstonks_api_key_requests_total',
    'Total requests to Riot API',
    ['endpoint', 'status_code']
)

RATE_LIMIT_HITS = Counter(
    'lolstonks_rate_limit_hits_total',
    'Number of rate limit hits',
    ['endpoint', 'region']
)

def timed(histogram):
    """Decorator to measure function execution time."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                histogram.observe(time.time() - start_time)
                return result
            except Exception as e:
                histogram.observe(time.time() - start_time)
                raise
        return wrapper
    return decorator
```

## Alerting

> **Not Implemented**: Alerting is not currently configured. The examples below show potential configurations.

### Alert Configuration (Example)

```yaml
# alerts.yml
groups:
  - name: lolstonks_critical
    rules:
      - alert: ServiceDown
        expr: up{job="lolstonks-api"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "LOLStonks API Gateway is down"
          description: "Service has been down for more than 1 minute"

      - alert: HighErrorRate
        expr: rate(lolstonks_requests_total{status!~"2.."}[5m]) / rate(lolstonks_requests_total[5m]) > 0.1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }}"

  - name: lolstonks_warnings
    rules:
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(lolstonks_request_duration_seconds_bucket[5m])) > 1.0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time detected"
          description: "95th percentile response time is {{ $value }}s"

      - alert: LowCacheHitRate
        expr: lolstonks_cache_hit_rate < 0.7
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Low cache hit rate"
          description: "Cache hit rate is {{ $value | humanizePercentage }}"
```

### Notification Channels

```yaml
# alertmanager.yml
global:
  smtp_smarthost: 'localhost:587'
  smtp_from: 'alerts@yourdomain.com'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
  - name: 'web.hook'
    email_configs:
      - to: 'team@yourdomain.com'
        subject: '[LOLStonks Alert] {{ .GroupLabels.alertname }}'
        body: |
          {{ range .Alerts }}
          Alert: {{ .Annotations.summary }}
          Description: {{ .Annotations.description }}
          {{ end }}

    slack_configs:
      - api_url: 'YOUR_SLACK_WEBHOOK_URL'
        channel: '#alerts'
        title: 'LOLStonks Alert'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
```

---

## Summary

This document outlines **best practices and potential implementations** for comprehensive monitoring.

**Current State**: The API Gateway has basic logging (Loguru) and a simple health check endpoint.

**Future Enhancements**: Implementing Prometheus metrics, Grafana dashboards, ELK stack, and OpenTelemetry would provide full observability and enable proactive issue detection and performance optimization.

For the actual implementation status, see [Implementation Status](implementation-status.md).
