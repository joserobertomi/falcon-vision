# Configuration Guide

## Overview

This guide covers all configuration options for Falcon Vision, including environment variables, database settings, authentication, and performance tuning.

## Environment Configuration

### Backend Configuration

#### Database Settings
```bash
# Primary database connection
DATABASE_URL=postgresql://username:password@localhost:5432/falcon_vision

# Alternative database settings
DB_HOST=localhost
DB_PORT=5432
DB_NAME=falcon_vision
DB_USER=postgres
DB_PASSWORD=password
DB_SSL_MODE=prefer
```

#### Authentication Settings
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
```

#### Email Configuration
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

#### Application Settings
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

### Frontend Configuration

#### API Settings
```bash
# API endpoints
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
VITE_API_TIMEOUT=30000

# Alternative API settings
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_BASE_URL=ws://localhost:8000/ws
```

#### Application Settings
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

#### Feature Flags
```bash
# Feature toggles
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_WEBSOCKET=true
VITE_ENABLE_DARK_MODE=true
VITE_ENABLE_NOTIFICATIONS=true
VITE_ENABLE_OFFLINE_MODE=false
```

### UI Dashboard Configuration

#### API Settings
```bash
# Backend API
API_BASE_URL=http://localhost:8000
API_TIMEOUT=30000
API_RETRY_ATTEMPTS=3
```

#### Dashboard Settings
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

## Database Configuration

### PostgreSQL Settings

#### Connection Settings
```bash
# Connection parameters
POSTGRES_DB=falcon_vision
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# SSL Configuration
POSTGRES_SSL_MODE=prefer
POSTGRES_SSL_CERT=
POSTGRES_SSL_KEY=
POSTGRES_SSL_ROOT_CERT=
```

#### Performance Settings
```sql
-- postgresql.conf
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

#### Connection Pooling
```bash
# Connection pool settings
POSTGRES_POOL_SIZE=20
POSTGRES_MAX_OVERFLOW=30
POSTGRES_POOL_TIMEOUT=30
POSTGRES_POOL_RECYCLE=3600
```

### Redis Configuration

#### Connection Settings
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

#### Cache Settings
```bash
# Cache configuration
REDIS_CACHE_TTL=300
REDIS_CACHE_PREFIX=falcon_vision:
REDIS_CACHE_MAX_SIZE=1000
```

## Computer Vision Configuration

### Model Settings
```bash
# Model configuration
MODEL_PATH=models/yolov8n.pt
CONFIDENCE_THRESHOLD=0.5
NMS_THRESHOLD=0.45
MAX_DETECTIONS=100
INPUT_SIZE=640

# Performance settings
GPU_ENABLED=true
BATCH_SIZE=1
FRAME_SKIP=1
MAX_FPS=30
```

### Detection Parameters
```python
# Detection configuration
DETECTION_CONFIG = {
    "model_path": "models/yolov8n.pt",
    "confidence_threshold": 0.5,
    "nms_threshold": 0.45,
    "max_detections": 100,
    "input_size": (640, 640),
    "classes": [0],  # Person class only
    "device": "cuda" if torch.cuda.is_available() else "cpu"
}
```

## Security Configuration

### Authentication Security
```bash
# JWT Security
JWT_SECRET_KEY=your-super-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Password Security
PASSWORD_HASH_ROUNDS=12
PASSWORD_MIN_LENGTH=8
PASSWORD_REQUIRE_UPPERCASE=true
PASSWORD_REQUIRE_LOWERCASE=true
PASSWORD_REQUIRE_DIGITS=true
PASSWORD_REQUIRE_SPECIAL_CHARS=false
```

### CORS Security
```bash
# CORS Configuration
CORS_ORIGINS=["https://your-domain.com", "https://api.your-domain.com"]
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
CORS_ALLOW_HEADERS=["Authorization", "Content-Type", "X-Requested-With"]
CORS_EXPOSE_HEADERS=["X-Total-Count"]
CORS_MAX_AGE=3600
```

### Rate Limiting
```bash
# Rate limiting
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_BURST=10
RATE_LIMIT_STORAGE_URL=redis://localhost:6379/1
```

## Performance Configuration

### Backend Performance
```bash
# Server settings
WORKERS=4
MAX_REQUESTS=1000
MAX_REQUESTS_JITTER=100
TIMEOUT=30
KEEP_ALIVE=2
GRACEFUL_TIMEOUT=30

# Database settings
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
```

### Frontend Performance
```bash
# Build settings
VITE_BUILD_SOURCEMAP=false
VITE_BUILD_MINIFY=true
VITE_BUILD_TARGET=es2015

# Bundle settings
VITE_BUNDLE_ANALYZER=false
VITE_CHUNK_SIZE_WARNING_LIMIT=1000
```

### Caching Configuration
```bash
# Cache settings
CACHE_TTL=300
CACHE_MAX_SIZE=1000
CACHE_PREFIX=falcon_vision:
CACHE_BACKEND=redis
```

## Monitoring Configuration

### Logging Settings
```bash
# Logging configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=/var/log/falcon-vision/app.log
LOG_ROTATION=daily
LOG_RETENTION_DAYS=30
LOG_COMPRESSION=true
```

### Metrics Settings
```bash
# Metrics configuration
ENABLE_METRICS=true
METRICS_PORT=9090
METRICS_PATH=/metrics
METRICS_INTERVAL=15
```

### Health Check Settings
```bash
# Health check configuration
HEALTH_CHECK_INTERVAL=30
HEALTH_CHECK_TIMEOUT=10
HEALTH_CHECK_RETRIES=3
```

## Email Configuration

### SMTP Settings
```bash
# SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_TLS=true
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@your-domain.com
SMTP_FROM_NAME="Falcon Vision"
```

### Email Templates
```bash
# Email template settings
EMAIL_TEMPLATES_DIR=app/email-templates
EMAIL_TEMPLATES_ENGINE=jinja2
EMAIL_TEMPLATES_AUTO_RELOAD=true
```

### Email Notifications
```bash
# Notification settings
EMAIL_NOTIFICATIONS_ENABLED=true
EMAIL_NOTIFICATIONS_FROM=noreply@your-domain.com
EMAIL_NOTIFICATIONS_TO=admin@your-domain.com
```

## File Storage Configuration

### Local Storage
```bash
# Local file storage
UPLOAD_DIR=/var/lib/falcon-vision/uploads
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_FILE_TYPES=["image/jpeg", "image/png", "image/webp"]
FILE_STORAGE_BACKEND=local
```

### S3 Storage
```bash
# S3 configuration
S3_BUCKET=your-bucket-name
S3_REGION=us-east-1
S3_ACCESS_KEY_ID=your-access-key
S3_SECRET_ACCESS_KEY=your-secret-key
S3_ENDPOINT_URL=https://s3.amazonaws.com
```

### MinIO Storage
```bash
# MinIO configuration
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=falcon-vision
MINIO_SECURE=false
```

## WebSocket Configuration

### WebSocket Settings
```bash
# WebSocket configuration
WS_HOST=0.0.0.0
WS_PORT=8000
WS_PATH=/ws
WS_MAX_CONNECTIONS=100
WS_PING_INTERVAL=30
WS_PING_TIMEOUT=10
```

### Real-time Settings
```bash
# Real-time configuration
REALTIME_ENABLED=true
REALTIME_BROADCAST_INTERVAL=1
REALTIME_MAX_FRAME_SIZE=1048576  # 1MB
REALTIME_COMPRESSION=true
```

## Development Configuration

### Development Settings
```bash
# Development configuration
DEBUG=true
LOG_LEVEL=DEBUG
ENVIRONMENT=development
RELOAD=true
AUTO_RELOAD=true
```

### Testing Settings
```bash
# Test configuration
TESTING=true
TEST_DATABASE_URL=postgresql://postgres:password@localhost:5432/falcon_vision_test
TEST_LOG_LEVEL=WARNING
TEST_TIMEOUT=30
```

### Development Tools
```bash
# Development tools
ENABLE_PROFILER=true
ENABLE_DEBUG_TOOLBAR=true
ENABLE_SQL_LOGGING=true
ENABLE_REQUEST_LOGGING=true
```

## Production Configuration

### Production Settings
```bash
# Production configuration
DEBUG=false
LOG_LEVEL=INFO
ENVIRONMENT=production
RELOAD=false
AUTO_RELOAD=false
```

### Security Settings
```bash
# Production security
SECRET_KEY=your-super-secret-production-key
JWT_SECRET_KEY=your-super-secret-jwt-production-key
ALLOWED_HOSTS=["your-domain.com", "api.your-domain.com"]
```

### Performance Settings
```bash
# Production performance
WORKERS=4
MAX_REQUESTS=1000
TIMEOUT=30
KEEP_ALIVE=2
GRACEFUL_TIMEOUT=30
```

## Configuration Validation

### Backend Validation
```python
# Configuration validation
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
// Frontend configuration validation
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

## Configuration Management

### Environment Files
```bash
# Development
.env.development

# Production
.env.production

# Testing
.env.testing

# Local override
.env.local
```

### Configuration Loading
```python
# Configuration loading
import os
from pathlib import Path

def load_config():
    env = os.getenv('ENVIRONMENT', 'development')
    config_file = f'.env.{env}'
    
    if Path(config_file).exists():
        load_dotenv(config_file)
    
    # Load local override
    if Path('.env.local').exists():
        load_dotenv('.env.local')
```

## Best Practices

### Security Best Practices
1. Use strong, unique secrets for each environment
2. Never commit `.env` files to version control
3. Use environment-specific configuration files
4. Validate all configuration values
5. Use least privilege principle

### Performance Best Practices
1. Tune database connection pools
2. Configure appropriate cache settings
3. Set proper worker counts
4. Enable compression where appropriate
5. Monitor resource usage

### Maintenance Best Practices
1. Document all configuration changes
2. Use configuration management tools
3. Test configuration changes in staging
4. Keep configuration files organized
5. Regular configuration audits