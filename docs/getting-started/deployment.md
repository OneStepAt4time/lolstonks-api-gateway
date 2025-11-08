# Production Deployment

This guide covers deploying the LOLStonks API Gateway to production environments with proper security, monitoring, and scalability considerations.

## Prerequisites

### System Requirements

- **CPU**: 2+ cores (4+ recommended for high traffic)
- **RAM**: 4GB+ (8GB+ recommended for production)
- **Storage**: 20GB+ SSD for logs and caching
- **Network**: Stable internet connection with low latency to Riot API servers
- **Operating System**: Linux (Ubuntu 20.04+, CentOS 8+, or similar)

### External Dependencies

- **Redis Server**: 6.0+ for caching and session management
- **Reverse Proxy**: Nginx 1.18+ or similar for SSL termination
- **Process Manager**: systemd, supervisor, or similar
- **SSL Certificate**: Valid SSL certificate for HTTPS

## Installation

### 1. System Preparation

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required system packages
sudo apt install -y python3.12 python3.12-venv python3-pip nginx redis-server

# Create application user
sudo useradd -m -s /bin/bash lolstonks
sudo usermod -aG sudo lolstonks
```

### 2. Application Setup

```bash
# Switch to application user
sudo su - lolstonks

# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc

# Clone the repository
git clone https://github.com/OneStepAt4time/lolstonks-api-gateway.git
cd lolstonks-api-gateway

# Install dependencies
uv pip install -e ".[docs]"

# Create environment file
cp .env.example .env
nano .env  # Edit with your configuration
```

### 3. Environment Configuration

Create a secure `.env` file:

```env
# Production Configuration
# Option 1: Single key (basic)
RIOT_API_KEY=RGAPI-your-production-api-key

# Option 2: Multiple keys (recommended for production)
# RIOT_API_KEYS=RGAPI-prod-key-1,RGAPI-prod-key-2,RGAPI-prod-key-3

RIOT_DEFAULT_REGION=euw1

# Server Configuration
HOST=127.0.0.1
PORT=8080
LOG_LEVEL=INFO
ENVIRONMENT=production

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=your-redis-password

# Rate Limiting (adjust based on your API key limits)
RIOT_RATE_LIMIT_PER_SECOND=20
RIOT_RATE_LIMIT_PER_2MIN=100

# Security
CORS_ORIGINS=https://yourdomain.com
ALLOWED_HOSTS=yourdomain.com

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090
```

## Process Management

### Systemd Service (Recommended)

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/lolstonks-api.service
```

```ini
[Unit]
Description=LOLStonks API Gateway
After=network.target redis.service

[Service]
Type=exec
User=lolstonks
Group=lolstonks
WorkingDirectory=/home/lolstonks/lolstonks-api-gateway
Environment=PATH=/home/lolstonks/.local/bin:/usr/local/bin:/usr/bin:/bin
EnvironmentFile=/home/lolstonks/lolstonks-api-gateway/.env
ExecStart=/home/lolstonks/.local/bin/uv run uvicorn app.main:app --host 0.0.0.0 --port 8080
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/home/lolstonks/lolstonks-api-gateway/logs

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable lolstonks-api.service
sudo systemctl start lolstonks-api.service
```

### Supervisor Alternative

If using supervisor, create `/etc/supervisor/conf.d/lolstonks-api.conf`:

```ini
[program:lolstonks-api]
command=/home/lolstonks/.local/bin/uv run uvicorn app.main:app --host 0.0.0.0 --port 8080
directory=/home/lolstonks/lolstonks-api-gateway
user=lolstonks
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/lolstonks/api.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
environment=PATH="/home/lolstonks/.local/bin:/usr/local/bin"
```

## Reverse Proxy Configuration

### Nginx Configuration

Create `/etc/nginx/sites-available/lolstonks-api`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";

    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;

        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }

    # Health endpoint (no rate limiting)
    location /health {
        proxy_pass http://127.0.0.1:8080/health;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API documentation
    location /docs {
        proxy_pass http://127.0.0.1:8080/docs;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/lolstonks-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Redis Configuration

### Production Redis Setup

Edit `/etc/redis/redis.conf`:

```conf
# Security
bind 127.0.0.1
requirepass your-redis-password
port 6379

# Memory management
maxmemory 2gb
maxmemory-policy allkeys-lru

# Persistence
save 900 1
save 300 10
save 60 10000

# Logging
logfile /var/log/redis/redis-server.log
loglevel notice

# Performance
tcp-keepalive 300
timeout 0
```

Restart Redis:

```bash
sudo systemctl restart redis-server
sudo systemctl enable redis-server
```

## SSL Certificate Setup

### Let's Encrypt (Recommended)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Set up auto-renewal
sudo crontab -e
# Add this line:
0 12 * * * /usr/bin/certbot renew --quiet
```

## Monitoring and Logging

### Log Management

Create log directories:

```bash
sudo mkdir -p /var/log/lolstonks
sudo chown lolstonks:lolstonks /var/log/lolstonks
```

Configure log rotation:

```bash
sudo nano /etc/logrotate.d/lolstonks-api
```

```
/var/log/lolstonks/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 lolstonks lolstonks
    postrotate
        systemctl reload lolstonks-api.service
    endscript
}
```

### Health Monitoring

Set up monitoring for the health endpoint:

```bash
# Simple monitoring script
cat > /home/lolstonks/health_check.sh << 'EOF'
#!/bin/bash
HEALTH_URL="http://127.0.0.1:8080/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ $RESPONSE -ne 200 ]; then
    echo "Health check failed with status $RESPONSE"
    # Send alert (configure your preferred alerting method)
    systemctl restart lolstonks-api.service
fi
EOF

chmod +x /home/lolstonks/health_check.sh

# Add to crontab for monitoring every minute
echo "* * * * * /home/lolstonks/health_check.sh" | crontab -u lolstonks -
```

## Performance Optimization

### System Tuning

```bash
# Increase file descriptor limits
echo "lolstonks soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "lolstonks hard nofile 65536" | sudo tee -a /etc/security/limits.conf

# Optimize network settings
echo "net.core.somaxconn = 65535" | sudo tee -a /etc/sysctl.conf
echo "net.ipv4.tcp_max_syn_backlog = 65535" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### Application Performance

Update `.env` for production:

```env
# Performance settings
UVICORN_WORKERS=4  # Number of worker processes
UVICORN_WORKER_CONNECTIONS=1000
UVICORN_BACKLOG=2048

# Caching settings
CACHE_TTL_SUMMONER=3600    # 1 hour
CACHE_TTL_MATCH=86400      # 24 hours
CACHE_TTL_LEAGUE=1800      # 30 minutes
```

## Security Hardening

### Firewall Configuration

```bash
# Configure UFW firewall
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH (change port if needed)
sudo ufw allow ssh

# Allow HTTP/HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Allow Redis only locally
sudo ufw allow from 127.0.0.1 to any port 6379
```

### Application Security

1. **API Key Rotation**: Use multiple API keys with `RIOT_API_KEYS` for automatic rotation. The gateway uses round-robin rotation across all provided keys to distribute load and provide redundancy.
2. **Input Validation**: Ensure all inputs are validated (handled by Pydantic)
3. **Rate Limiting**: Configure appropriate rate limits
4. **Access Controls**: Implement IP whitelisting if needed
5. **Regular Updates**: Keep system and dependencies updated

## Backup and Recovery

### Configuration Backup

```bash
# Create backup script
cat > /home/lolstonks/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/lolstonks/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup configuration
tar -czf $BACKUP_DIR/config_$DATE.tar.gz \
    /home/lolstonks/lolstonks-api-gateway/.env \
    /etc/nginx/sites-available/lolstonks-api \
    /etc/systemd/system/lolstonks-api.service

# Keep last 7 days
find $BACKUP_DIR -name "config_*.tar.gz" -mtime +7 -delete
EOF

chmod +x /home/lolstonks/backup.sh

# Add to crontab for daily backup at 2 AM
echo "0 2 * * * /home/lolstonks/backup.sh" | crontab -u lolstonks -
```

### Disaster Recovery

1. **Documentation**: Keep deployment documentation updated
2. **Monitoring**: Set up alerts for service failures
3. **Backups**: Regular configuration and code backups
4. **Testing**: Regular disaster recovery testing

## Rollback Procedures

When a deployment fails or issues are discovered in production, you can rollback to a previous stable version using these procedures.

### Docker-based Rollback

If you're using Docker, rollback is straightforward:

```bash
# Stop the current container
docker-compose down

# Or if running standalone:
docker stop lolstonks-api
docker rm lolstonks-api

# Pull and run a specific previous version
docker pull ghcr.io/onestepat4time/lolstonks-api-gateway:2.0.0

# Using docker-compose, edit docker-compose.yml to specify the version:
# image: ghcr.io/onestepat4time/lolstonks-api-gateway:2.0.0

# Start with the previous version
docker-compose up -d

# Or standalone:
docker run -d \
  --name lolstonks-api \
  -p 8080:8080 \
  --env-file .env \
  ghcr.io/onestepat4time/lolstonks-api-gateway:2.0.0
```

### Git-based Rollback (Systemd/Native Deployment)

For native deployments using systemd:

```bash
# 1. Stop the service
sudo systemctl stop lolstonks-api.service

# 2. Navigate to application directory
cd /home/lolstonks/lolstonks-api-gateway

# 3. Identify the version to rollback to
git tag --list  # List all available versions
git log --oneline -n 10  # Or check recent commits

# 4. Rollback to a specific version tag
git checkout v2.0.0

# Or rollback to a specific commit
# git checkout <commit-hash>

# 5. Reinstall dependencies (if needed)
uv sync

# 6. Restart the service
sudo systemctl start lolstonks-api.service

# 7. Verify the rollback
sudo systemctl status lolstonks-api.service
curl http://127.0.0.1:8080/health

# 8. Check application version
curl http://127.0.0.1:8080/health | jq '.version'
```

### Emergency Rollback Script

Create an automated rollback script for faster recovery:

```bash
cat > /home/lolstonks/rollback.sh << 'EOF'
#!/bin/bash

# Emergency Rollback Script for LOLStonks API Gateway
# Usage: ./rollback.sh <version_tag>
# Example: ./rollback.sh v2.0.0

if [ -z "$1" ]; then
    echo "Usage: $0 <version_tag>"
    echo "Example: $0 v2.0.0"
    exit 1
fi

VERSION=$1
APP_DIR="/home/lolstonks/lolstonks-api-gateway"
BACKUP_DIR="/home/lolstonks/rollback_backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "🔄 Starting rollback to $VERSION..."

# Create backup of current state
echo "📦 Creating backup of current state..."
mkdir -p $BACKUP_DIR
cd $APP_DIR
CURRENT_VERSION=$(cat VERSION 2>/dev/null || echo "unknown")
git rev-parse HEAD > $BACKUP_DIR/pre_rollback_commit_$TIMESTAMP.txt
echo "$CURRENT_VERSION" > $BACKUP_DIR/pre_rollback_version_$TIMESTAMP.txt

# Stop the service
echo "⏹️  Stopping service..."
sudo systemctl stop lolstonks-api.service

# Verify the version exists
if ! git tag | grep -q "^$VERSION$"; then
    echo "❌ Error: Version tag $VERSION not found!"
    echo "Available versions:"
    git tag --list
    sudo systemctl start lolstonks-api.service
    exit 1
fi

# Checkout the specified version
echo "📥 Checking out version $VERSION..."
git fetch --tags
git checkout $VERSION

# Reinstall dependencies
echo "📦 Reinstalling dependencies..."
uv sync

# Start the service
echo "▶️  Starting service..."
sudo systemctl start lolstonks-api.service

# Wait for service to start
sleep 5

# Verify the service is running
if systemctl is-active --quiet lolstonks-api.service; then
    echo "✅ Service is running"

    # Check health endpoint
    HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8080/health)
    if [ "$HEALTH_CHECK" = "200" ]; then
        echo "✅ Health check passed"
        echo "✅ Rollback to $VERSION completed successfully!"
        echo ""
        echo "Rolled back from: $CURRENT_VERSION"
        echo "Rolled back to: $VERSION"
        echo "Backup location: $BACKUP_DIR/pre_rollback_*_$TIMESTAMP.txt"
    else
        echo "⚠️  Warning: Service started but health check failed (HTTP $HEALTH_CHECK)"
        echo "Check logs: sudo journalctl -u lolstonks-api.service -n 50"
    fi
else
    echo "❌ Error: Service failed to start after rollback"
    echo "Check logs: sudo journalctl -u lolstonks-api.service -n 50"
    exit 1
fi
EOF

chmod +x /home/lolstonks/rollback.sh
```

### Docker Rollback Script

For Docker deployments:

```bash
cat > /home/lolstonks/docker-rollback.sh << 'EOF'
#!/bin/bash

# Docker Rollback Script for LOLStonks API Gateway
# Usage: ./docker-rollback.sh <version>
# Example: ./docker-rollback.sh 2.0.0

if [ -z "$1" ]; then
    echo "Usage: $0 <version>"
    echo "Example: $0 2.0.0"
    echo ""
    echo "Available versions:"
    docker pull ghcr.io/onestepat4time/lolstonks-api-gateway:latest 2>/dev/null
    echo "Check: https://github.com/OneStepAt4time/lolstonks-api-gateway/pkgs/container/lolstonks-api-gateway"
    exit 1
fi

VERSION=$1
IMAGE="ghcr.io/onestepat4time/lolstonks-api-gateway:$VERSION"

echo "🔄 Starting Docker rollback to version $VERSION..."

# Stop current container
echo "⏹️  Stopping current container..."
docker-compose down || docker stop lolstonks-api

# Pull the specified version
echo "📥 Pulling version $VERSION..."
if ! docker pull $IMAGE; then
    echo "❌ Error: Failed to pull image $IMAGE"
    echo "Check if version exists: https://github.com/OneStepAt4time/lolstonks-api-gateway/releases"
    exit 1
fi

# Update docker-compose.yml to use specific version
echo "📝 Updating docker-compose.yml..."
sed -i.bak "s|image:.*lolstonks-api-gateway:.*|image: $IMAGE|g" docker-compose.yml

# Start with the new version
echo "▶️  Starting container with version $VERSION..."
docker-compose up -d

# Wait for container to be healthy
echo "⏳ Waiting for container to be healthy..."
sleep 10

# Check health
HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8080/health)
if [ "$HEALTH_CHECK" = "200" ]; then
    echo "✅ Rollback to version $VERSION completed successfully!"
    echo "✅ Health check passed"
    docker-compose ps
else
    echo "⚠️  Warning: Health check failed (HTTP $HEALTH_CHECK)"
    echo "Container logs:"
    docker-compose logs --tail=50 app
fi
EOF

chmod +x /home/lolstonks/docker-rollback.sh
```

### Rollback Verification Checklist

After performing a rollback, verify the following:

1. **Service Status**: Confirm the service is running
   ```bash
   sudo systemctl status lolstonks-api.service
   # Or for Docker:
   docker-compose ps
   ```

2. **Health Check**: Verify the health endpoint responds
   ```bash
   curl http://127.0.0.1:8080/health
   ```

3. **Version Verification**: Confirm the correct version is running
   ```bash
   curl http://127.0.0.1:8080/health | jq '.version'
   ```

4. **Functionality Test**: Test critical endpoints
   ```bash
   # Test a simple endpoint
   curl http://127.0.0.1:8080/api/v1/summoner/by-name/euw1/test
   ```

5. **Log Review**: Check for errors in recent logs
   ```bash
   sudo journalctl -u lolstonks-api.service -n 100 --no-pager
   # Or for Docker:
   docker-compose logs --tail=100 app
   ```

6. **Redis Connectivity**: Verify Redis connection
   ```bash
   redis-cli -a your-password ping
   ```

7. **External Access**: Test through Nginx/load balancer
   ```bash
   curl https://yourdomain.com/health
   ```

### Preventing Future Rollbacks

To minimize the need for rollbacks:

1. **Staging Environment**: Always test releases in staging first
2. **Gradual Rollout**: Use canary or blue-green deployments for critical changes
3. **Automated Testing**: Ensure comprehensive test coverage before release
4. **Monitoring**: Set up alerts to detect issues quickly
5. **Release Notes**: Maintain detailed changelog and release notes
6. **Database Migrations**: Always use reversible database migrations
7. **Feature Flags**: Use feature flags to disable problematic features without rollback

### Database Migration Rollback

If your rollback includes database schema changes:

```bash
# This project currently uses Redis (no schema migrations)
# But if you add a SQL database later, use migration tools like Alembic:

# Example with Alembic (for future reference):
# alembic downgrade -1  # Rollback one migration
# alembic downgrade <revision>  # Rollback to specific revision
```

### Emergency Hotfix Process

If a critical bug is found in production:

1. **Create hotfix branch** from the production tag:
   ```bash
   git checkout -b hotfix/critical-bug-fix v2.0.0
   ```

2. **Apply minimal fix** and test thoroughly

3. **Version bump** using patch version:
   ```bash
   python scripts/bump_version.py patch
   ```

4. **Create hotfix tag**:
   ```bash
   git tag -a v2.0.1 -m "Hotfix: Critical bug fix"
   git push origin hotfix/critical-bug-fix
   git push --tags
   ```

5. **Deploy hotfix** immediately

6. **Merge back** to develop and main branches

## Scaling Considerations

### Horizontal Scaling

For high-traffic deployments:

1. **Load Balancer**: Use HAProxy or cloud load balancer
2. **Multiple Instances**: Run multiple API gateway instances
3. **Redis Cluster**: Use Redis cluster for distributed caching
4. **Database Sharding**: Consider database sharding if needed

### Performance Monitoring

Monitor key metrics:
- Request rate and response times
- Error rates and types
- Cache hit rates
- Memory and CPU usage
- Redis performance

## Troubleshooting

### Common Issues

1. **Service Won't Start**: Check logs with `journalctl -u lolstonks-api.service`
2. **High Memory Usage**: Check Redis memory usage and adjust limits
3. **Slow Responses**: Check rate limiting and cache performance
4. **API Errors**: Verify Riot API key and rate limits

### Debug Commands

```bash
# Check service status
sudo systemctl status lolstonks-api.service

# View logs
sudo journalctl -u lolstonks-api.service -f

# Check Redis
redis-cli -a your-password ping

# Test API locally
curl http://127.0.0.1:8080/health

# Check Nginx configuration
sudo nginx -t

# Monitor system resources
htop
iostat -x 1
```

This deployment guide provides a comprehensive foundation for running the LOLStonks API Gateway in production with proper security, monitoring, and scalability considerations.
