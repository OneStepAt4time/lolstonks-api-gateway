# Architecture

This document summarizes the gateway's major components and responsibilities.

## Components


Design notes


Deployment

## Diagrams

### High-level flow

```mermaid
flowchart LR
	Client -->|HTTP| API[FastAPI Gateway]
	API -->|cache lookup| Redis[Redis Cache]
	API -->|rate-limited request| Riot[Riot API]
	Riot -->|response| API
	API -->|store processed match id| Redis
```

### Request sequence (match fetch)

```mermaid
sequenceDiagram
	participant C as Client
	participant G as Gateway
	participant R as Redis
	participant Riot as Riot API

	C->>G: GET /lol/match/v5/matches/by-puuid/{puuid}/ids
	G->>R: check cached ids
	alt cache hit
		R-->>G: ids
		G-->>C: return ids
	else cache miss
		G->>Riot: request ids (rate-limited)
		Riot-->>G: ids
		G->>R: cache ids
		G-->>C: return ids
	end
```
- For production: run behind a process manager / reverse proxy, ensure env var provisioning and secrets management are in place.
