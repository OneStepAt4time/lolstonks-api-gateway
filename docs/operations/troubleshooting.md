# Troubleshooting Guide

This comprehensive troubleshooting guide helps diagnose and resolve common issues with the LOLStonks API Gateway.

## Table of Contents

- [Service Issues](#service-issues)
- [Performance Problems](#performance-problems)
- [Cache and Redis Issues](#cache-and-redis-issues)
- [API and Rate Limiting Issues](#api-and-rate-limiting-issues)
- [Network and Connectivity Issues](#network-and-connectivity-issues)
- [Configuration Issues](#configuration-issues)
- [Monitoring and Debugging](#monitoring-and-debugging)

## Service Issues

### Service Won't Start

#### Symptoms
- Service fails to start or crashes immediately
- `systemctl status lolstonks-api.service` shows failed state
- No response from health endpoint

#### Diagnosis Steps

1. **Check Service Status**
```bash
sudo systemctl status lolstonks-api.service
```

2. **View Service Logs**
```bash
# View recent logs
sudo journalctl -u lolstonks-api.service -n 50

# Follow logs in real-time
sudo journalctl -u lolstonks-api.service -f
```

3. **Check Configuration**
```bash
# Verify environment file exists and is readable
sudo -u lolstonks cat /home/lolstonks/lolstonks-api-gateway/.env

# Test configuration manually
sudo -u lolstonks cd /home/lolstonks/lolstonks-api-gateway
sudo -u lolstonks uv run python -c "from app.config import settings; print(settings.dict())"
```

#### Common Causes and Solutions

**Missing Dependencies**
```bash
# Reinstall dependencies
sudo -u lolstonks cd /home/lolstonks/lolstonks-api-gateway
sudo -u lolstonks uv pip install -e ".[docs]"
```

**Permission Issues**
```bash
# Fix ownership
sudo chown -R lolstonks:lolstonks /home/lolstonks/lolstonks-api-gateway

# Fix permissions
sudo chmod +x /home/lolstonks/lolstonks-api-gateway/scripts/*.py
```

**Port Already in Use**
```bash
# Check what's using the port
sudo netstat -tulpn | grep :8080

# Kill the process using the port
sudo kill -9 <PID>
```

**Invalid Configuration**
```bash
# Validate environment variables
sudo -u lolstonks bash -c 'source .env && echo "Configuration valid"'
```

### Service Crashes or Restarts

#### Symptoms
- Service runs for a while then crashes
- Frequent automatic restarts
- Out of memory errors

#### Diagnosis

1. **Check Memory Usage**
```bash
# Monitor memory usage
htop

# Check OOM killer logs
sudo dmesg | grep -i "killed process"
```

2. **Check for Memory Leaks**
```bash
# Monitor over time
while true; do
    echo "$(date): $(ps -o pid,ppid,cmd,%mem,%cpu -p $(pgrep -f uvicorn))"
    sleep 30
done
```

#### Solutions

**Increase Memory Limits**
```bash
# Edit service file to increase memory limits
sudo nano /etc/systemd/system/lolstonks-api.service
# Add:
# MemoryLimit=2G
# MemorySwap=2G
```

**Optimize Configuration**
```env
# In .env file
UVICORN_WORKERS=2  # Reduce worker count
CACHE_SIZE_LIMIT=1000000  # Reduce cache size
```

## Performance Problems

### Slow Response Times

#### Symptoms
- API responses taking >5 seconds
- Timeouts from client applications
- High latency on specific endpoints

#### Diagnosis

1. **Benchmark Response Times**
```bash
# Test response time
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8080/health

# Create curl-format.txt:
#      time_namelookup:  %{time_namelookup}\n
#         time_connect:  %{time_connect}\n
#      time_appconnect:  %{time_appconnect}\n
#     time_pretransfer:  %{time_pretransfer}\n
#        time_redirect:  %{time_redirect}\n
#   time_starttransfer:  %{time_starttransfer}\n
#                      ----------\n
#           time_total:  %{time_total}\n
```

2. **Profile the Application**
```bash
# Install profiling tools
uv pip install py-spy

# Profile CPU usage
sudo py-spy top --pid $(pgrep -f uvicorn)

# Generate flame graph
sudo py-spy record --pid $(pgrep -f uvicorn) -o profile.svg --duration 60
```

3. **Check Resource Utilization**
```bash
# CPU and memory
top
htop

# Disk I/O
iostat -x 1

# Network I/O
iftop
```

#### Common Causes and Solutions

**High CPU Usage**
- **Cause**: Too many concurrent requests, inefficient code
- **Solution**:
  - Reduce worker count: `UVICORN_WORKERS=2`
  - Implement caching: Increase cache TTL
  - Optimize database queries

**High Memory Usage**
- **Cause**: Memory leaks, large cache sizes
- **Solution**:
  - Reduce cache size: `CACHE_SIZE_LIMIT=500000`
  - Restart service periodically
  - Profile memory usage

**Network Latency**
- **Cause**: Slow network to Riot API, DNS resolution issues
- **Solution**:
  - Use faster DNS servers: 8.8.8.8, 1.1.1.1
  - Consider CDN or regional deployment
  - Implement connection pooling

### High Error Rates

#### Symptoms
- 5xx errors increasing
- 429 rate limit errors
- Timeouts from Riot API

#### Diagnosis

1. **Check Error Logs**
```bash
# Filter for errors
sudo journalctl -u lolstonks-api.service | grep -i error

# Check specific error types
sudo journalctl -u lolstonks-api.service | grep "429\|500\|502\|503"
```

2. **Monitor Riot API Status**
```bash
# Test Riot API directly
curl -H "X-Riot-Token: YOUR_API_KEY" \
     https://euw1.api.riotgames.com/lol/status/v4/platform-data

# Check status page
curl https://status.riotgames.com/
```

#### Solutions

**Rate Limiting (429 Errors)**
```env
# Reduce rate limits in .env
RIOT_RATE_LIMIT_PER_SECOND=15  # Reduce from 20
RIOT_RATE_LIMIT_PER_2MIN=80    # Reduce from 100
```

**Riot API Outages**
- **Solution**: Monitor Riot API status, implement circuit breakers
- **Monitoring**: Set up alerts for API status changes

**Timeout Errors**
```env
# Increase timeouts in .env
RIOT_REQUEST_TIMEOUT=30
RIOT_MAX_RETRIES=5
```

## Cache and Redis Issues

### Cache Misses or Invalidation

#### Symptoms
- High rate of API calls to Riot servers
- Inconsistent data responses
- Poor performance

#### Diagnosis

1. **Check Redis Status**
```bash
# Test Redis connection
redis-cli -a YOUR_PASSWORD ping

# Check memory usage
redis-cli -a YOUR_PASSWORD info memory

# Check hit rate
redis-cli -a YOUR_PASSWORD info stats | grep keyspace
```

2. **Monitor Cache Performance**
```bash
# Check cache keys
redis-cli -a YOUR_PASSWORD keys "lolstonks:*" | wc -l

# Monitor cache operations
redis-cli -a YOUR_PASSWORD monitor
```

#### Solutions

**Redis Connection Issues**
```bash
# Check Redis service
sudo systemctl status redis-server

# Restart Redis if needed
sudo systemctl restart redis-server

# Check Redis configuration
sudo redis-cli -a YOUR_PASSWORD config get "*"
```

**Cache Eviction**
```env
# Increase Redis memory limit
# In redis.conf:
maxmemory 4gb
maxmemory-policy allkeys-lru
```

**Invalid Cache Keys**
```bash
# Clear corrupted cache
redis-cli -a YOUR_PASSWORD flushdb

# Restart application to rebuild cache
sudo systemctl restart lolstonks-api.service
```

### Redis Memory Issues

#### Symptoms
- Redis using excessive memory
- Out of memory errors
- Slow Redis operations

#### Diagnosis

```bash
# Check Redis memory usage
redis-cli -a YOUR_PASSWORD info memory | grep used_memory_human

# Check largest keys
redis-cli -a YOUR_PASSWORD --bigkeys

# Monitor memory usage over time
watch -n 1 'redis-cli -a YOUR_PASSWORD info memory | grep used_memory_human'
```

#### Solutions

**Memory Optimization**
```conf
# In redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
```

**Key Expiration**
```bash
# Set TTL on existing keys
redis-cli -a YOUR_PASSWORD --eval - <<EOF
for _, key in ipairs(redis.call('keys', 'lolstonks:*')) do
  redis.call('expire', key, 3600)
end
EOF
```

## API and Rate Limiting Issues

### Rate Limiting Problems

#### Symptoms
- 429 errors from Riot API
- Requests being throttled
- Poor user experience

#### Diagnosis

1. **Check Current Rate Limits**
```bash
# Monitor rate limiting in logs
sudo journalctl -u lolstonks-api.service | grep -i "rate.*limit"

# Check API usage dashboard on Riot Developer Portal
```

2. **Test Rate Limiting**
```bash
# Quick test script
for i in {1..25}; do
  curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8080/health
  sleep 0.1
done
```

#### Solutions

**Adjust Rate Limits**
```env
# Conservative rate limits
RIOT_RATE_LIMIT_PER_SECOND=10
RIOT_RATE_LIMIT_PER_2MIN=80
```

**Implement Request Batching**
```python
# Batch multiple requests into single API calls
# This reduces overall API usage
```

**Add Request Queuing**
```python
# Implement request queue for high-traffic periods
```

### Invalid API Responses

#### Symptoms
- Corrupted or incomplete data
- Invalid JSON responses
- Missing fields in API responses

#### Diagnosis

1. **Validate API Response**
```bash
# Test specific endpoint
curl -s http://localhost:8080/summoner/by-name/test?region=euw1 | jq .

# Check response headers
curl -I http://localhost:8080/summoner/by-name/test?region=euw1
```

2. **Check Data Validation**
```bash
# Test with invalid data
curl -s http://localhost:8080/summoner/by-name/invalid@name?region=euw1
```

#### Solutions

**Update Pydantic Models**
- **Cause**: Riot API changed response format
- **Solution**: Update models in `app/models/` to match new format

**Implement Data Sanitization**
```python
# Add data cleaning in API routers
def clean_summoner_data(data):
    # Remove or fix invalid fields
    return cleaned_data
```

## Network and Connectivity Issues

### DNS Resolution Problems

#### Symptoms
- Slow startup times
- Intermittent connection failures
- DNS timeout errors

#### Diagnosis

```bash
# Test DNS resolution
nslookup euw1.api.riotgames.com
dig euw1.api.riotgames.com

# Test with different DNS servers
nslookup euw1.api.riotgames.com 8.8.8.8
nslookup euw1.api.riotgames.com 1.1.1.1
```

#### Solutions

**Use Reliable DNS Servers**
```bash
# Edit /etc/resolv.conf
nameserver 8.8.8.8
nameserver 1.1.1.1
nameserver 208.67.222.222
```

**Implement DNS Caching**
```bash
# Install dnsmasq for local DNS caching
sudo apt install dnsmasq
sudo systemctl enable dnsmasq
sudo systemctl start dnsmasq
```

### SSL/TLS Issues

#### Symptoms
- Certificate errors
- SSL handshake failures
- HTTPS connection issues

#### Diagnosis

```bash
# Test SSL connection
openssl s_client -connect euw1.api.riotgames.com:443

# Check certificate validity
curl -v https://euw1.api.riotgames.com/lol/status/v4/platform-data
```

#### Solutions

**Update CA Certificates**
```bash
sudo apt update && sudo apt install ca-certificates
```

**Configure SSL Properly**
```bash
# Ensure system time is correct
sudo timedatectl set-ntp true

# Update SSL libraries
sudo apt install openssl libssl-dev
```

## Configuration Issues

### Environment Variable Problems

#### Symptoms
- Service won't start
- Invalid configuration values
- Runtime errors

#### Diagnosis

```bash
# Check environment file syntax
cat .env | bash -n

# Test configuration loading
sudo -u lolstonks bash -c 'source .env && env | grep RIOT'

# Validate required variables
grep -E "^(RIOT_API_KEY|REDIS_HOST)" .env
```

#### Solutions

**Fix Environment File**
```bash
# Backup and recreate
cp .env .env.backup
nano .env

# Ensure proper format:
# KEY=value
# No quotes around values unless needed
```

**Missing Required Variables**
```bash
# Add missing variables to .env
echo "RIOT_API_KEY=RGAPI-your-key-here" >> .env
echo "REDIS_HOST=localhost" >> .env
```

### Permissions Issues

#### Symptoms
- Permission denied errors
- File access issues
- Service startup failures

#### Diagnosis

```bash
# Check file permissions
ls -la /home/lolstonks/lolstonks-api-gateway/

# Check user permissions
sudo -u lolstonks whoami
sudo -u lolstonks ls -la

# Check systemd service user
grep "User\|Group" /etc/systemd/system/lolstonks-api.service
```

#### Solutions

**Fix Ownership**
```bash
# Set correct ownership
sudo chown -R lolstonks:lolstonks /home/lolstonks/lolstonks-api-gateway
```

**Fix Permissions**
```bash
# Set appropriate permissions
sudo chmod 755 /home/lolstonks/lolstonks-api-gateway
sudo chmod 644 /home/lolstonks/lolstonks-api-gateway/.env
sudo chmod +x /home/lolstonks/lolstonks-api-gateway/scripts/*.py
```

## Monitoring and Debugging

### Health Check Script

Create a comprehensive health monitoring script:

```bash
#!/bin/bash
# health_check.sh

API_URL="http://127.0.0.1:8080/health"
REDIS_CLI="redis-cli -a YOUR_PASSWORD"
LOG_FILE="/var/log/lolstonks/health_check.log"

# Function to log with timestamp
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Check API health
check_api() {
    local response=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL")
    if [ "$response" != "200" ]; then
        log "API health check failed with status: $response"
        return 1
    fi
    return 0
}

# Check Redis health
check_redis() {
    local pong=$($REDIS_CLI ping 2>/dev/null)
    if [ "$pong" != "PONG" ]; then
        log "Redis health check failed"
        return 1
    fi
    return 0
}

# Check system resources
check_resources() {
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    local mem_usage=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')

    if (( $(echo "$cpu_usage > 80" | bc -l) )); then
        log "High CPU usage: ${cpu_usage}%"
    fi

    if (( $(echo "$mem_usage > 80" | bc -l) )); then
        log "High memory usage: ${mem_usage}%"
    fi
}

# Main health check
main() {
    log "Starting health check"

    if ! check_api; then
        log "Restarting API service"
        sudo systemctl restart lolstonks-api.service
    fi

    if ! check_redis; then
        log "Restarting Redis service"
        sudo systemctl restart redis-server
    fi

    check_resources

    log "Health check completed"
}

main
```

### Log Analysis Script

Create a log analysis script for troubleshooting:

```bash
#!/bin/bash
# analyze_logs.sh

LOG_FILE="/var/log/lolstonks/api.log"
ERROR_PATTERN="(ERROR|CRITICAL|Exception|Traceback)"
WARNING_PATTERN="(WARNING|WARN)"

echo "=== Error Analysis ==="
grep -E "$ERROR_PATTERN" "$LOG_FILE" | tail -20

echo -e "\n=== Warning Analysis ==="
grep -E "$WARNING_PATTERN" "$LOG_FILE" | tail -20

echo -e "\n=== Response Time Analysis ==="
grep "response_time" "$LOG_FILE" | tail -20 | awk '{print $NF}' | sort -n

echo -e "\n=== Top Error Endpoints ==="
grep "ERROR" "$LOG_FILE" | awk '{print $6}' | sort | uniq -c | sort -nr | head -10
```

### Performance Monitoring

Set up basic performance monitoring:

```bash
#!/bin/bash
# monitor.sh

API_PID=$(pgrep -f uvicorn)

if [ -z "$API_PID" ]; then
    echo "API service not running"
    exit 1
fi

echo "=== CPU and Memory Usage ==="
ps -p "$API_PID" -o pid,ppid,cmd,%mem,%cpu

echo -e "\n=== File Descriptors ==="
lsof -p "$API_PID" | wc -l

echo -e "\n=== Network Connections ==="
netstat -p | grep "$API_PID" | wc -l

echo -e "\n=== Redis Memory Usage ==="
redis-cli -a YOUR_PASSWORD info memory | grep used_memory_human
```

This comprehensive troubleshooting guide should help diagnose and resolve most common issues with the LOLStonks API Gateway. For issues not covered here, check the service logs and consider reaching out to the development team.
