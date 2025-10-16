# Production Deployment

## Overview

This guide covers deploying Falcon Vision in a production environment with high availability, security, and performance considerations.

## Prerequisites

### Infrastructure Requirements
- **Server**: Ubuntu 20.04+ or CentOS 8+
- **Resources**: 8GB RAM, 4 CPU cores minimum
- **Storage**: 100GB SSD minimum
- **Network**: Static IP address, domain name
- **SSL Certificate**: Let's Encrypt or commercial certificate

### Software Requirements
- **Docker**: 20.10+ with BuildKit
- **Docker Compose**: 2.0+
- **Nginx**: 1.18+ (reverse proxy)
- **PostgreSQL**: 13+ (external database)
- **Redis**: 6+ (caching and sessions)

## Architecture

### Production Stack
```
Internet
    ↓
[Load Balancer] (Nginx/HAProxy)
    ↓
[Reverse Proxy] (Traefik)
    ↓
[Application Layer]
├── Backend API (FastAPI)
├── Frontend (React)
├── UI Dashboard (Streamlit)
└── Documentation (MkDocs)
    ↓
[Data Layer]
├── PostgreSQL (Primary)
├── Redis (Cache)
└── File Storage (S3/MinIO)
```

### High Availability Setup
- **Load Balancer**: Multiple Nginx instances
- **Application**: Multiple backend/frontend instances
- **Database**: Primary-replica setup
- **Cache**: Redis cluster
- **Storage**: Distributed file system

## Server Setup

### 1. Initial Server Configuration
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y curl wget git nginx certbot python3-certbot-nginx

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Firewall Configuration
```bash
# Configure UFW
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable

# Check status
sudo ufw status
```

### 3. SSL Certificate Setup
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com -d api.your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Database Setup

### PostgreSQL Configuration
```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE falcon_vision;
CREATE USER falcon_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE falcon_vision TO falcon_user;
\q

# Configure PostgreSQL
sudo nano /etc/postgresql/13/main/postgresql.conf
```

### PostgreSQL Production Settings
```conf
# postgresql.conf
listen_addresses = 'localhost'
port = 5432
max_connections = 200
shared_buffers = 2GB
effective_cache_size = 6GB
maintenance_work_mem = 512MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
```

### Redis Configuration
```bash
# Install Redis
sudo apt install redis-server

# Configure Redis
sudo nano /etc/redis/redis.conf
```

### Redis Production Settings
```conf
# redis.conf
bind 127.0.0.1
port 6379
timeout 300
tcp-keepalive 300
maxmemory 1gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

## Application Deployment

### 1. Clone and Configure
```bash
# Clone repository
git clone https://github.com/falcon-vision/falcon-vision.git
cd falcon-vision

# Copy production configuration
cp .env.example .env.production

# Edit environment variables
nano .env.production
```

### 2. Production Environment Variables
```bash
# .env.production
# Database
DATABASE_URL=postgresql://falcon_user:secure_password@localhost:5432/falcon_vision

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-super-secret-jwt-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# CORS
CORS_ORIGINS=["https://your-domain.com", "https://api.your-domain.com"]

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_TLS=true
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAILS_FROM_EMAIL=noreply@your-domain.com

# Production
DEBUG=false
LOG_LEVEL=INFO
ENVIRONMENT=production

# API
API_V1_STR=/api/v1
PROJECT_NAME=Falcon Vision

# Security
SECRET_KEY=your-super-secret-key-here
ALLOWED_HOSTS=["your-domain.com", "api.your-domain.com"]

# File Storage
UPLOAD_DIR=/var/lib/falcon-vision/uploads
MAX_FILE_SIZE=10485760  # 10MB
```

### 3. Production Docker Compose
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  backend:
    build: ./backend
    restart: unless-stopped
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - DEBUG=false
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
      - ./uploads:/app/uploads
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G

  frontend:
    build: ./frontend
    restart: unless-stopped
    environment:
      - VITE_API_URL=https://api.your-domain.com
      - NODE_ENV=production
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:80"]
      interval: 30s
      timeout: 10s
      retries: 3

  ui:
    build: ./ui
    restart: unless-stopped
    environment:
      - API_BASE_URL=https://api.your-domain.com
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5174"]
      interval: 30s
      timeout: 10s
      retries: 3

  proxy:
    image: traefik:v3.0
    restart: unless-stopped
    command:
      - --api.dashboard=true
      - --providers.docker=true
      - --entrypoints.web.address=:80
      - --entrypoints.websecure.address=:443
      - --certificatesresolvers.letsencrypt.acme.tlschallenge=true
      - --certificatesresolvers.letsencrypt.acme.email=admin@your-domain.com
      - --certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json
      - --providers.docker.exposedbydefault=false
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./letsencrypt:/letsencrypt
    labels:
      - traefik.enable=true
      - traefik.http.routers.traefik.rule=Host(`traefik.your-domain.com`)
      - traefik.http.routers.traefik.tls.certresolver=letsencrypt
      - traefik.http.routers.traefik.service=api@internal

networks:
  default:
    external: true
    name: falcon-vision-network
```

### 4. Nginx Configuration
```nginx
# /etc/nginx/sites-available/falcon-vision
upstream backend {
    server 127.0.0.1:8000;
}

upstream frontend {
    server 127.0.0.1:5173;
}

upstream ui {
    server 127.0.0.1:5174;
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket
    location /ws/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # UI Dashboard
    location /ui/ {
        proxy_pass http://ui;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files
    location /static/ {
        alias /var/lib/falcon-vision/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Uploads
    location /uploads/ {
        alias /var/lib/falcon-vision/uploads/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## Monitoring and Logging

### 1. Log Management
```bash
# Create log directory
sudo mkdir -p /var/log/falcon-vision
sudo chown -R $USER:$USER /var/log/falcon-vision

# Configure logrotate
sudo nano /etc/logrotate.d/falcon-vision
```

### Logrotate Configuration
```
/var/log/falcon-vision/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 $USER $USER
    postrotate
        docker-compose restart backend
    endscript
}
```

### 2. Monitoring Setup
```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'

  grafana:
    image: grafana/grafana
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources

  node-exporter:
    image: prom/node-exporter
    restart: unless-stopped
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.rootfs=/rootfs'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'

volumes:
  prometheus_data:
  grafana_data:
```

### 3. Health Checks
```bash
#!/bin/bash
# health-check.sh

# Check backend health
if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "Backend health check failed"
    exit 1
fi

# Check frontend health
if ! curl -f http://localhost:5173 > /dev/null 2>&1; then
    echo "Frontend health check failed"
    exit 1
fi

# Check database connection
if ! docker-compose exec -T db pg_isready -U postgres > /dev/null 2>&1; then
    echo "Database health check failed"
    exit 1
fi

echo "All health checks passed"
```

## Backup Strategy

### 1. Database Backup
```bash
#!/bin/bash
# backup-db.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/falcon-vision"
DB_NAME="falcon_vision"
DB_USER="falcon_user"

# Create backup directory
mkdir -p $BACKUP_DIR

# Create database backup
docker-compose exec -T db pg_dump -U $DB_USER $DB_NAME > $BACKUP_DIR/db_backup_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/db_backup_$DATE.sql

# Remove backups older than 30 days
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +30 -delete

echo "Database backup completed: db_backup_$DATE.sql.gz"
```

### 2. Application Backup
```bash
#!/bin/bash
# backup-app.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/falcon-vision"
APP_DIR="/opt/falcon-vision"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup application files
tar -czf $BACKUP_DIR/app_backup_$DATE.tar.gz -C $APP_DIR .

# Backup uploads
tar -czf $BACKUP_DIR/uploads_backup_$DATE.tar.gz -C /var/lib/falcon-vision/uploads .

# Remove backups older than 30 days
find $BACKUP_DIR -name "app_backup_*.tar.gz" -mtime +30 -delete
find $BACKUP_DIR -name "uploads_backup_*.tar.gz" -mtime +30 -delete

echo "Application backup completed: app_backup_$DATE.tar.gz"
```

### 3. Automated Backup
```bash
# Add to crontab
crontab -e

# Add these lines:
0 2 * * * /opt/falcon-vision/scripts/backup-db.sh
0 3 * * * /opt/falcon-vision/scripts/backup-app.sh
```

## Security Hardening

### 1. System Security
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install fail2ban
sudo apt install fail2ban

# Configure fail2ban
sudo nano /etc/fail2ban/jail.local
```

### Fail2ban Configuration
```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
maxretry = 3

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 3
```

### 2. Docker Security
```bash
# Create non-root user
sudo useradd -r -s /bin/false falcon-vision

# Set proper permissions
sudo chown -R falcon-vision:falcon-vision /opt/falcon-vision
sudo chmod -R 755 /opt/falcon-vision
```

### 3. Application Security
```bash
# Set secure file permissions
chmod 600 .env.production
chmod 600 /etc/letsencrypt/live/your-domain.com/privkey.pem

# Enable firewall
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
```

## Performance Optimization

### 1. Database Optimization
```sql
-- Create indexes
CREATE INDEX idx_detections_timestamp ON detections(timestamp);
CREATE INDEX idx_detections_user_id ON detections(user_id);
CREATE INDEX idx_detections_confidence ON detections(confidence);

-- Analyze tables
ANALYZE detections;
ANALYZE users;
```

### 2. Application Optimization
```yaml
# docker-compose.prod.yml
services:
  backend:
    environment:
      - WORKERS=4
      - MAX_REQUESTS=1000
      - MAX_REQUESTS_JITTER=100
      - TIMEOUT=30
      - KEEP_ALIVE=2
```

### 3. Caching Configuration
```python
# backend/app/core/config.py
CACHE_TTL = 300  # 5 minutes
CACHE_MAX_SIZE = 1000
CACHE_PREFIX = "falcon_vision:"
```

## Maintenance

### 1. Regular Maintenance Tasks
```bash
#!/bin/bash
# maintenance.sh

# Update system
sudo apt update && sudo apt upgrade -y

# Clean Docker
docker system prune -f

# Restart services
docker-compose restart

# Check logs
docker-compose logs --tail=100

echo "Maintenance completed"
```

### 2. Update Procedure
```bash
#!/bin/bash
# update.sh

# Pull latest changes
git pull origin main

# Backup current version
./scripts/backup-app.sh

# Update services
docker-compose pull
docker-compose up -d

# Run migrations
docker-compose exec backend alembic upgrade head

# Verify deployment
./scripts/health-check.sh

echo "Update completed"
```

## Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check logs
docker-compose logs backend

# Check resources
docker stats

# Check configuration
docker-compose config
```

#### Database Connection Issues
```bash
# Check database status
docker-compose exec db pg_isready -U postgres

# Check database logs
docker-compose logs db

# Test connection
docker-compose exec backend python -c "from app.database import engine; print(engine.connect())"
```

#### SSL Certificate Issues
```bash
# Check certificate status
sudo certbot certificates

# Renew certificate
sudo certbot renew

# Test SSL
openssl s_client -connect your-domain.com:443
```

### Emergency Procedures

#### Rollback
```bash
# Stop current services
docker-compose down

# Restore from backup
./scripts/restore-backup.sh

# Start services
docker-compose up -d
```

#### Disaster Recovery
```bash
# Restore database
gunzip -c /var/backups/falcon-vision/db_backup_20240101_020000.sql.gz | docker-compose exec -T db psql -U postgres falcon_vision

# Restore application
tar -xzf /var/backups/falcon-vision/app_backup_20240101_030000.tar.gz -C /opt/falcon-vision/

# Start services
docker-compose up -d
```
