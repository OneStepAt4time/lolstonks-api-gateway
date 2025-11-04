# API Key Rotation Feature

## Overview

The gateway now supports **multiple Riot API keys** with automatic **round-robin rotation** to distribute load and help manage rate limits more effectively.

## Configuration

### Option 1: Single Key (Backward Compatible)

```bash
# .env file
RIOT_API_KEY=RGAPI-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

### Option 2: Multiple Keys with Rotation (Recommended)

```bash
# .env file
RIOT_API_KEYS=RGAPI-key1,RGAPI-key2,RGAPI-key3
```

**Note:** If both `RIOT_API_KEYS` and `RIOT_API_KEY` are set, `RIOT_API_KEYS` takes priority.

## How It Works

### 1. Configuration Loading

The `Settings` class (`app/config.py`) now supports both variables:

```python
riot_api_key: str | None = None  # Backward compatible
riot_api_keys: str | None = None  # New - comma-separated
```

The `get_api_keys()` method returns a list of keys with priority:
1. `RIOT_API_KEYS` (if set) - comma-separated list
2. `RIOT_API_KEY` (fallback) - single key
3. Raises `ValueError` if neither is set

### 2. Key Rotation Logic

The `KeyRotator` class (`app/riot/key_rotator.py`) implements thread-safe round-robin rotation:

- **Algorithm:** Circular iteration through keys
- **Thread-Safety:** Uses `threading.Lock` for concurrent access
- **Logging:** Logs key usage (masked for security)

Example:
```python
rotator = KeyRotator(["key1", "key2", "key3"])
rotator.get_next_key()  # Returns "key1"
rotator.get_next_key()  # Returns "key2"
rotator.get_next_key()  # Returns "key3"
rotator.get_next_key()  # Returns "key1" (wraps around)
```

### 3. RiotClient Integration

The `RiotClient` (`app/riot/client.py`) now:
- Initializes `KeyRotator` with configured keys
- Gets next key on each API request
- Injects key into request header dynamically

```python
# Get next key from rotator
api_key = self.key_rotator.get_next_key()

# Make request with rotated key
headers = {"X-Riot-Token": api_key}
response = await self.client.get(url, params=params, headers=headers)
```

## Benefits

1. **Load Distribution:** Requests are evenly distributed across all keys
2. **Better Rate Limit Management:** Multiple keys = higher total rate limit
3. **Redundancy:** If one key is exhausted, others are still available
4. **Zero Downtime:** No application restart needed to add/remove keys
5. **Backward Compatible:** Existing single-key setups continue to work

## Testing

### Unit Tests

Run the key rotation test suite:

```bash
cd lolstonks-api-gateway
uv run pytest tests/test_key_rotation.py -v
```

Test coverage:
- ✅ KeyRotator class (round-robin, thread-safety, reset)
- ✅ Settings.get_api_keys() (priority, parsing, validation)
- ✅ RiotClient integration

### Manual Testing

1. **Configure multiple keys:**
```bash
# .env
RIOT_API_KEYS=RGAPI-key1,RGAPI-key2
```

2. **Start server:**
```bash
make run
```

3. **Verify logs:**
```
Key rotator initialized with 2 API keys
Riot API client initialized with 2 API keys
```

4. **Make API calls:**
```bash
curl "http://127.0.0.1:8080/lol/platform/v3/champion-rotations?region=euw1"
```

5. **Check logs (DEBUG level):**
```
Selected API key: RGAPI-841c8046...
Selected API key: RGAPI-39074647...
```

## Migration Guide

### From Single Key to Multiple Keys

**Before:**
```bash
RIOT_API_KEY=RGAPI-841c8046-63f0-4037-aa0a-42003f3ae67d
```

**After:**
```bash
# Option 1: Keep single key (backward compatible)
RIOT_API_KEY=RGAPI-841c8046-63f0-4037-aa0a-42003f3ae67d

# Option 2: Add multiple keys (recommended)
RIOT_API_KEYS=RGAPI-841c8046-63f0-4037-aa0a-42003f3ae67d,RGAPI-39074647-c7c5-4a22-8b64-9e1a4d7eddd7
```

**No code changes required!** Just update `.env` and restart the gateway.

## Production Recommendations

1. **Use at least 2 keys** for redundancy
2. **Monitor key usage** via logs (set `LOG_LEVEL=DEBUG`)
3. **Rotate keys periodically** for security (update .env and restart)
4. **Test failover** by temporarily removing keys from .env

## FAQ

### Q: How many keys can I configure?
**A:** No hard limit, but 2-5 keys is typical. More keys = more management overhead.

### Q: Can I hot-reload keys without restarting?
**A:** Not yet. You need to restart the gateway for key changes to take effect.

### Q: What happens if all keys hit rate limits?
**A:** The gateway's internal rate limiter (20 req/s, 100 req/2min) prevents this. If Riot API returns 429, the client automatically retries after the specified delay.

### Q: Does rotation affect caching?
**A:** No. Caching is independent of which key is used. Cache keys are based on endpoint and parameters, not API key.

### Q: Can I use keys from different Riot accounts?
**A:** Yes, but ensure all keys have the same rate limit tier. Mixing Development and Production keys is not recommended.

## Implementation Details

### Files Modified

1. **app/config.py** - Added `riot_api_keys` field and `get_api_keys()` method
2. **app/riot/key_rotator.py** - **NEW** - Rotation logic
3. **app/riot/client.py** - Updated to use KeyRotator
4. **tests/test_key_rotation.py** - **NEW** - Test coverage
5. **.env.example** - Documented new configuration

### Backward Compatibility

- ✅ Existing single-key configurations work unchanged
- ✅ No breaking changes to API
- ✅ No changes required in client applications

## Monitoring

**Startup logs:**
```
Key rotator initialized with X API keys
Riot API client initialized with X API keys
```

**Request logs (DEBUG level):**
```
Selected API key: RGAPI-841c8046...
```

**Enable DEBUG logging:**
```bash
# .env
LOG_LEVEL=DEBUG
```

---

**Feature Status:** ✅ Implemented and Tested
**Version:** 1.1.0
**Date:** 2025-11-04
