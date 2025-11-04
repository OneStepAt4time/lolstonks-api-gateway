# Architecture

This document outlines the architecture of the LOL API Gateway, an intelligent proxy for the Riot Games API.

## Components

The system is composed of three main components:

*   **API Gateway:** A FastAPI application that serves as the entry point for all API requests. It handles request routing, caching, and rate limiting.
*   **Redis Cache:** A Redis instance used for caching API responses and tracking match data.
*   **Riot API Client:** An HTTP client for communicating with the official Riot Games API.

## Technology Stack

The following technologies are used to build and run the application:

*   **Python 3.12:** The programming language used for the application.
*   **FastAPI:** A modern, fast (high-performance) web framework for building APIs with Python 3.12+ based on standard Python type hints.
*   **Uvicorn:** A lightning-fast ASGI server implementation, using uvloop and httptools.
*   **Redis:** An in-memory data structure store, used as a database, cache, and message broker.
*   **Docker:** A platform for developing, shipping, and running applications in containers.
*   **uv:** A fast Python package installer and resolver, written in Rust.

## Application Structure

The application is structured as follows:

```
app/
├── __init__.py
├── config.py           # Configuration management
├── main.py             # FastAPI application entry point
├── cache/
│   ├── __init__.py
│   ├── redis_cache.py  # Redis cache implementation
│   └── tracking.py     # Match tracking functionality
├── riot/
│   ├── __init__.py
│   ├── client.py       # Riot API client
│   ├── rate_limiter.py # Rate limiting for Riot API
│   └── regions.py      # Riot API regions
└── routers/
    ├── __init__.py
    ├── account.py
    ├── challenges.py
    ├── champion_mastery.py
    ├── champion.py
    ├── clash.py
    ├── health.py
    ├── league.py
    ├── match.py
    ├── platform.py
    ├── spectator.py
    └── summoner.py
```

*   **`main.py`:** The main entry point of the application. It initializes the FastAPI app, includes the routers, and manages the application's lifespan.
*   **`config.py`:** Manages the application's configuration using Pydantic Settings.
*   **`cache/`:** Contains the caching and tracking logic.
    *   **`redis_cache.py`:** Implements a Redis-based cache for API responses.
    *   **`tracking.py`:** Provides functionality for tracking matches.
*   **`riot/`:** Contains the logic for interacting with the Riot Games API.
    *   **`client.py`:** The HTTP client for the Riot API.
    *   **`rate_limiter.py`:** A rate limiter to comply with the Riot API's rate limits.
    *   **`regions.py`:** Defines the available Riot API regions.
*   **`routers/`:** Contains the API endpoints, with each file corresponding to a different set of endpoints from the Riot API.

## API Endpoints

The API Gateway exposes the same endpoints as the official Riot Games API, allowing it to act as a transparent proxy. The available endpoints are defined in the `routers/` directory.

## Deployment



The application is designed to be deployed using Docker. The `docker-compose.yml` file defines two services:



*   **`redis`:** The Redis cache.

*   **`app`:** The FastAPI application.



The application is containerized using the provided `Dockerfile`. It uses `uv` to install dependencies and `uvicorn` to run the application.



## Detailed Components



### Riot API Client



The `RiotClient` class in `app/riot/client.py` is responsible for all communication with the Riot Games API. It provides the following features:



*   **Asynchronous Requests:** Uses `httpx` to make asynchronous HTTP requests, allowing for high performance.

*   **Rate Limiting:** Uses `aiolimiter` to enforce the Riot API's rate limits, preventing 429 errors.

*   **Automatic Retries:** Automatically retries requests that fail with a 429 status code, after waiting for the duration specified in the `Retry-After` header.

*   **Region-Aware Routing:** Automatically selects the correct base URL for the specified region.

*   **Authentication:** Automatically includes the Riot API key in all requests.



### Redis Cache







The application uses `aiocache` to cache responses from the Riot API. The cache is configured in `app/cache/redis_cache.py` and has the following features:







*   **Redis Backend:** Uses Redis as the cache backend, providing a fast and persistent cache.



*   **JSON Serialization:** Uses a `JsonSerializer` to store Python objects in Redis.



*   **Time-to-Live (TTL):** Each cached item has a TTL, after which it is automatically evicted from the cache. The TTLs are configurable in the `app/config.py` file.



*   **Namespace:** All cache keys are prefixed with a namespace to avoid collisions with other applications using the same Redis instance.







### Match Tracking







The application implements a dual-layer match tracking system to prevent processing the same match multiple times:







*   **TTL Cache:** A TTL-based cache is used to store recently processed match IDs.



*   **Redis SET:** A Redis SET is used for permanent storage of all processed match IDs.







This system ensures that matches are not re-processed, even if the TTL cache is cleared.







## Design Goals







The following are the main design goals of the project:







*   **Decoupling:** Keep client callers decoupled from Riot's rate and cache concerns.



*   **Performance:** Let Redis provide the fast-path for repeated lookups.



*   **Resilience:** Provide transparent retry behavior for 429s so clients don't need to re-implement it.







## Roadmap







The following features are planned for future releases:







*   **Metrics and Tracing:** Add support for Prometheus and OpenTelemetry.



*   **Admin Endpoints:** Create endpoints for inspecting and flushing caches.



*   **Pluggable Storage Backends:** Allow for different storage backends for match tracking.



*   **Automatic API Key Rotation:** Add support for automatic API key rotation.
