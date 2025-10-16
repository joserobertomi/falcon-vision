# Environment Variables

## Overview

Falcon Vision uses environment variables for configuration across all components. This document provides a comprehensive reference for all environment variables.

## Backend Environment Variables

### Database Configuration
```bash
# Primary database connection
DATABASE_URL=postgresql://username:password@localhost:5432/falcon_vision

# Alternative database settings (if not using DATABASE_URL)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=falcon_vision
DB_USER=postgres
DB_PASSWORD=password
DB_SSL_MODE=prefer
```

### Authentication & Security
```bash
# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Password Hashing
PASSWORD_HASH_ROUNDS=12

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173", "https://your-domain.com"]
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
CORS_ALLOW_HEADERS=["*"]

# Security
SECRET_KEY=your-super-secret-key-here
ALLOWED_HOSTS=["localhost", "127.0.0.1", "your-domain.com"]
```

### Email Configuration
```bash
# SMTP Settings
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_TLS=true
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@your-domain.com
SMTP_FROM_NAME="Falcon Vision"

# Email Templates
EMAIL_TEMPLATES_DIR=app/email-templates
EMAILS_FROM_EMAIL=noreply@your-domain.com
EMAILS_FROM_NAME="Falcon Vision"
```

### Redis Configuration
```bash
# Redis connection
REDIS_URL=redis://localhost:6379/0

# Alternative Redis settings
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
REDIS_SSL=false
```

### Application Settings
```bash
# General
PROJECT_NAME=Falcon Vision
API_V1_STR=/api/v1
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=4
RELOAD=false

# File Upload
UPLOAD_DIR=/var/lib/falcon-vision/uploads
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_FILE_TYPES=["image/jpeg", "image/png", "image/webp"]
```

### Computer Vision Settings
```bash
# Model Configuration
MODEL_PATH=models/yolov8n.pt
CONFIDENCE_THRESHOLD=0.5
NMS_THRESHOLD=0.45
MAX_DETECTIONS=100
INPUT_SIZE=640

# Performance
GPU_ENABLED=true
BATCH_SIZE=1
FRAME_SKIP=1
MAX_FPS=30
```

### Monitoring & Logging
```bash
# Logging
LOG_FORMAT=json
LOG_FILE=/var/log/falcon-vision/app.log
LOG_ROTATION=daily
LOG_RETENTION_DAYS=30

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090
HEALTH_CHECK_INTERVAL=30
```

## Frontend Environment Variables

### API Configuration
```bash
# API endpoints
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
VITE_API_TIMEOUT=30000

# Alternative API settings
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_BASE_URL=ws://localhost:8000/ws
```

### Application Settings
```bash
# General
VITE_APP_NAME=Falcon Vision
VITE_APP_DESCRIPTION="Computer vision application with person detection"

# Environment
NODE_ENV=production
VITE_ENVIRONMENT=production
VITE_DEBUG=false
VITE_LOG_LEVEL=info
```

### Feature Flags
```bash
# Feature toggles
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_WEBSOCKET=true
VITE_ENABLE_DARK_MODE=true
VITE_ENABLE_NOTIFICATIONS=true
VITE_ENABLE_OFFLINE_MODE=false
```

### UI Configuration
```bash
# Theme
VITE_THEME=light
VITE_PRIMARY_COLOR=#3182ce
VITE_SECONDARY_COLOR=#805ad5

# Layout
VITE_SIDEBAR_WIDTH=250
VITE_HEADER_HEIGHT=60
VITE_FOOTER_HEIGHT=40
```

### External Services
```bash
# Analytics
VITE_GOOGLE_ANALYTICS_ID=GA-XXXXXXXXX
VITE_MIXPANEL_TOKEN=your-mixpanel-token

# Maps
VITE_GOOGLE_MAPS_API_KEY=your-google-maps-key

# Storage
VITE_S3_BUCKET=your-s3-bucket
VITE_S3_REGION=us-east-1
```

## UI Dashboard Environment Variables

### API Configuration
```bash
# Backend API
API_BASE_URL=http://localhost:8000
API_TIMEOUT=30000
API_RETRY_ATTEMPTS=3
```

### Application Settings
```bash
# General
APP_NAME=Falcon Vision Analytics
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Server
HOST=0.0.0.0
PORT=5174
RELOAD=false
```

### Dashboard Configuration
```bash
# Display settings
DASHBOARD_TITLE=Falcon Vision Analytics
DASHBOARD_DESCRIPTION="Real-time person detection analytics"
DASHBOARD_THEME=light
DASHBOARD_LAYOUT=wide

# Data refresh
REFRESH_INTERVAL=30
AUTO_REFRESH=true
CACHE_TTL=300
```

### Chart Configuration
```bash
# Chart settings
CHART_COLORS=["#3182ce", "#805ad5", "#38a169", "#e53e3e"]
CHART_ANIMATION=true
CHART_RESPONSIVE=true
CHART_HEIGHT=400
```

## Database Environment Variables

### PostgreSQL Configuration
```bash
# Connection
POSTGRES_DB=falcon_vision
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# SSL
POSTGRES_SSL_MODE=prefer
POSTGRES_SSL_CERT=
POSTGRES_SSL_KEY=
POSTGRES_SSL_ROOT_CERT=

# Connection Pool
POSTGRES_POOL_SIZE=20
POSTGRES_MAX_OVERFLOW=30
POSTGRES_POOL_TIMEOUT=30
POSTGRES_POOL_RECYCLE=3600
```

### Redis Configuration
```bash
# Connection
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
REDIS_SSL=false

# Pool
REDIS_POOL_SIZE=20
REDIS_POOL_TIMEOUT=30
REDIS_POOL_RECYCLE=3600

# Cache
REDIS_CACHE_TTL=300
REDIS_CACHE_PREFIX=falcon_vision:
REDIS_CACHE_MAX_SIZE=1000
```

## Proxy Environment Variables

### Traefik Configuration
```bash
# General
TRAEFIK_LOG_LEVEL=INFO
TRAEFIK_ACCESS_LOG=true
TRAEFIK_DEBUG=false

# API
TRAEFIK_API_DASHBOARD=true
TRAEFIK_API_INSECURE=false

# Entry Points
TRAEFIK_ENTRYPOINT_WEB_ADDRESS=:80
TRAEFIK_ENTRYPOINT_WEBSECURE_ADDRESS=:443

# Certificates
TRAEFIK_CERTIFICATESRESOLVERS_LETSENCRYPT_ACME_EMAIL=admin@your-domain.com
TRAEFIK_CERTIFICATESRESOLVERS_LETSENCRYPT_ACME_STORAGE=/letsencrypt/acme.json
TRAEFIK_CERTIFICATESRESOLVERS_LETSENCRYPT_ACME_TLSCHALLENGE=true
```

### Nginx Configuration
```bash
# General
NGINX_WORKER_PROCESSES=auto
NGINX_WORKER_CONNECTIONS=1024
NGINX_KEEPALIVE_TIMEOUT=65

# Gzip
NGINX_GZIP=true
NGINX_GZIP_TYPES="text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript"

# Security
NGINX_SERVER_TOKENS=off
NGINX_X_FRAME_OPTIONS=DENY
NGINX_X_CONTENT_TYPE_OPTIONS=nosniff
```

## Monitoring Environment Variables

### Prometheus Configuration
```bash
# General
PROMETHEUS_CONFIG_FILE=/etc/prometheus/prometheus.yml
PROMETHEUS_STORAGE_PATH=/prometheus
PROMETHEUS_RETENTION_TIME=15d
PROMETHEUS_WEB_ENABLE_LIFECYCLE=true

# Scrape
PROMETHEUS_SCRAPE_INTERVAL=15s
PROMETHEUS_SCRAPE_TIMEOUT=10s
PROMETHEUS_EVALUATION_INTERVAL=15s
```

### Grafana Configuration
```bash
# General
GF_SECURITY_ADMIN_PASSWORD=admin
GF_USERS_ALLOW_SIGN_UP=false
GF_USERS_ALLOW_ORG_CREATE=false

# Database
GF_DATABASE_TYPE=sqlite3
GF_DATABASE_PATH=/var/lib/grafana/grafana.db

# Server
GF_SERVER_HTTP_PORT=3000
GF_SERVER_ROOT_URL=https://grafana.your-domain.com
```

## Development Environment Variables

### Development Settings
```bash
# General
DEBUG=true
LOG_LEVEL=DEBUG
ENVIRONMENT=development
RELOAD=true

# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/falcon_vision_dev

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173", "http://localhost:8080"]

# Email (Development)
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_TLS=false
EMAILS_FROM_EMAIL=noreply@localhost
```

### Testing Settings
```bash
# Test Database
TEST_DATABASE_URL=postgresql://postgres:password@localhost:5432/falcon_vision_test

# Test Settings
TESTING=true
TEST_LOG_LEVEL=WARNING
TEST_TIMEOUT=30
```

## Production Environment Variables

### Production Settings
```bash
# General
DEBUG=false
LOG_LEVEL=INFO
ENVIRONMENT=production
RELOAD=false

# Security
SECRET_KEY=your-super-secret-production-key
JWT_SECRET_KEY=your-super-secret-jwt-production-key
ALLOWED_HOSTS=["your-domain.com", "api.your-domain.com"]

# Performance
WORKERS=4
MAX_REQUESTS=1000
TIMEOUT=30
KEEP_ALIVE=2
```

### High Availability
```bash
# Load Balancer
LOAD_BALANCER_URL=https://your-domain.com
BACKEND_SERVERS=["backend1:8000", "backend2:8000", "backend3:8000"]

# Database
DATABASE_URL=postgresql://user:pass@db-primary:5432/falcon_vision
DATABASE_REPLICA_URL=postgresql://user:pass@db-replica:5432/falcon_vision
```

## Environment File Examples

### Development (.env.development)
```bash
# Backend
DATABASE_URL=postgresql://postgres:password@localhost:5432/falcon_vision_dev
JWT_SECRET_KEY=dev-secret-key
DEBUG=true
LOG_LEVEL=DEBUG
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]

# Frontend
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
VITE_DEBUG=true
NODE_ENV=development

# UI
API_BASE_URL=http://localhost:8000
DEBUG=true
LOG_LEVEL=DEBUG
```

### Production (.env.production)
```bash
# Backend
DATABASE_URL=postgresql://user:pass@db.example.com:5432/falcon_vision
JWT_SECRET_KEY=your-super-secret-production-key
DEBUG=false
LOG_LEVEL=INFO
CORS_ORIGINS=["https://your-domain.com", "https://api.your-domain.com"]

# Frontend
VITE_API_URL=https://api.your-domain.com
VITE_WS_URL=wss://api.your-domain.com
VITE_DEBUG=false
NODE_ENV=production

# UI
API_BASE_URL=https://api.your-domain.com
DEBUG=false
LOG_LEVEL=INFO
```

## Environment Variable Validation

### Backend Validation
```python
# backend/app/core/config.py
from pydantic import BaseSettings, validator

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    @validator('JWT_SECRET_KEY')
    def validate_jwt_secret(cls, v):
        if len(v) < 32:
            raise ValueError('JWT_SECRET_KEY must be at least 32 characters')
        return v
    
    @validator('LOG_LEVEL')
    def validate_log_level(cls, v):
        if v not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            raise ValueError('LOG_LEVEL must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL')
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True
```

### Frontend Validation
```typescript
// frontend/src/config/env.ts
interface EnvConfig {
  VITE_API_URL: string;
  VITE_WS_URL: string;
  VITE_DEBUG: boolean;
  NODE_ENV: string;
}

function validateEnv(): EnvConfig {
  const requiredVars = ['VITE_API_URL', 'VITE_WS_URL'];
  
  for (const varName of requiredVars) {
    if (!import.meta.env[varName]) {
      throw new Error(`Missing required environment variable: ${varName}`);
    }
  }
  
  return {
    VITE_API_URL: import.meta.env.VITE_API_URL,
    VITE_WS_URL: import.meta.env.VITE_WS_URL,
    VITE_DEBUG: import.meta.env.VITE_DEBUG === 'true',
    NODE_ENV: import.meta.env.NODE_ENV,
  };
}

export const env = validateEnv();
```

## Security Considerations

### Sensitive Variables
- Never commit `.env` files to version control
- Use strong, unique values for secrets
- Rotate secrets regularly
- Use environment-specific values
- Consider using secret management services

### Best Practices
- Use `.env.example` files for documentation
- Validate all environment variables
- Use different values for different environments
- Monitor for exposed secrets
- Use least privilege principle
