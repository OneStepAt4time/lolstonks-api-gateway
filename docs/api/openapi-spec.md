# OpenAPI Specification

The API documentation is rendered using **Redoc**, providing a clean and professional interface for exploring the API endpoints, parameters, and responses.

## Interactive Documentation

<redoc src="../data/openapi.json"/>

## Download Specification

You can download the raw OpenAPI specification in JSON format:

- [Download OpenAPI JSON](../data/openapi.json){ .md-button }

## API Overview

The LOLStonks API Gateway provides a comprehensive REST API for accessing Riot Games data with built-in caching, rate limiting, and enhanced functionality.

### Base URL

```
http://localhost:8000
```

### Authentication

The API requires a Riot Games API key passed via the `X-Riot-Token` header or configured in the server environment.

### Rate Limiting

The gateway implements intelligent rate limiting to comply with Riot Games API limits:
- Automatic retry with exponential backoff
- Request queuing
- Rate limit status in response headers

### Caching

Responses are cached in Redis with configurable TTL based on endpoint type:
- Static data: Long TTL (hours/days)
- Dynamic data: Short TTL (minutes)
- Real-time data: No cache or very short TTL

### Error Handling

Standard HTTP status codes are used:
- `200` - Success
- `400` - Bad Request
- `404` - Not Found
- `429` - Rate Limit Exceeded
- `500` - Internal Server Error
- `502` - Bad Gateway (Riot API error)
