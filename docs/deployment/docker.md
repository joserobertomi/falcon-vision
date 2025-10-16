# Docker Deployment

## Overview

Falcon Vision is fully containerized using Docker and Docker Compose, making it easy to deploy across different environments.

## Prerequisites

- **Docker**: 20.10+ with BuildKit support
- **Docker Compose**: 2.0+
- **Git**: For cloning the repository
- **Minimum Resources**: 4GB RAM, 2 CPU cores

## Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/falcon-vision/falcon-vision.git
cd falcon-vision
```

### 2. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

### 3. Start Services
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### 4. Verify Deployment
```bash
# Check service status
docker-compose ps

# Test API
curl http://localhost:8000/health

# Test frontend
curl http://localhost:5173
```

## Service Architecture

### Core Services
- **Backend**: FastAPI application (Port 8000)
- **Frontend**: React application (Port 5173)
- **UI**: Streamlit dashboard (Port 5174)
- **Database**: PostgreSQL (Port 5432)
- **Proxy**: Traefik reverse proxy (Port 80/443)

### Supporting Services
- **Mailcatcher**: Email testing (Port 1080)
- **Docs**: MkDocs documentation (Port 8001)
- **Playwright**: E2E testing

## Docker Compose Configuration

### Main Services
```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/falcon_vision
    depends_on:
      - db
    volumes:
      - ./backend:/app
      - ./backend/htmlcov:/app/htmlcov

  frontend:
    build: ./frontend
    ports:
      - "5173:80"
    environment:
      - VITE_API_URL=http://localhost:8000
    depends_on:
      - backend

  ui:
    build: ./ui
    ports:
      - "5174:5174"
    environment:
      - API_BASE_URL=http://backend:8000
    depends_on:
      - backend

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=falcon_vision
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
```

### Development Override
```yaml
# docker-compose.override.yml
version: '3.8'

services:
  backend:
    command: fastapi run --reload app/main.py
    volumes:
      - ./backend:/app
    environment:
      - DEBUG=true
      - LOG_LEVEL=DEBUG

  frontend:
    command: npm run dev
    volumes:
      - ./frontend:/app
      - /app/node_modules
```

## Environment Variables

### Backend Configuration
```bash
# Database
DATABASE_URL=postgresql://postgres:password@db:5432/falcon_vision

# JWT
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]

# Email
SMTP_HOST=mailcatcher
SMTP_PORT=1025
SMTP_TLS=false
EMAILS_FROM_EMAIL=noreply@example.com

# Development
DEBUG=false
LOG_LEVEL=INFO
```

### Frontend Configuration
```bash
# API Configuration
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000

# Environment
NODE_ENV=production
```

## Building Images

### Backend Image
```bash
# Build backend image
docker build -t falcon-vision-backend ./backend

# Build with specific tag
docker build -t falcon-vision-backend:v1.0.0 ./backend

# Build with build args
docker build --build-arg PYTHON_VERSION=3.10 -t falcon-vision-backend ./backend
```

### Frontend Image
```bash
# Build frontend image
docker build -t falcon-vision-frontend ./frontend

# Build with environment variables
docker build --build-arg VITE_API_URL=http://api.example.com -t falcon-vision-frontend ./frontend
```

### Multi-stage Build
```dockerfile
# backend/Dockerfile
FROM python:3.10 as builder

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.10-slim

# Copy dependencies
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages

# Copy application
COPY . /app
WORKDIR /app

CMD ["python", "main.py"]
```

## Production Deployment

### Production Configuration
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  backend:
    build: ./backend
    restart: unless-stopped
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - DEBUG=false
    volumes:
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build: ./frontend
    restart: unless-stopped
    environment:
      - VITE_API_URL=${API_URL}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:80"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:15
    restart: unless-stopped
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### SSL/TLS Configuration
```yaml
# docker-compose.traefik.yml
version: '3.8'

services:
  proxy:
    image: traefik:v3.0
    command:
      - --api.dashboard=true
      - --providers.docker=true
      - --entrypoints.web.address=:80
      - --entrypoints.websecure.address=:443
      - --certificatesresolvers.letsencrypt.acme.tlschallenge=true
      - --certificatesresolvers.letsencrypt.acme.email=admin@example.com
      - --certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./letsencrypt:/letsencrypt
    labels:
      - traefik.enable=true
      - traefik.http.routers.traefik.rule=Host(`traefik.example.com`)
      - traefik.http.routers.traefik.tls.certresolver=letsencrypt
```

## Monitoring and Logging

### Health Checks
```yaml
# Health check configuration
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### Logging Configuration
```yaml
# Logging configuration
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### Monitoring Stack
```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
```

## Backup and Recovery

### Database Backup
```bash
# Create backup
docker-compose exec db pg_dump -U postgres falcon_vision > backup.sql

# Restore backup
docker-compose exec -T db psql -U postgres falcon_vision < backup.sql

# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T db pg_dump -U postgres falcon_vision > "backup_${DATE}.sql"
```

### Volume Backup
```bash
# Backup volumes
docker run --rm -v falcon-vision_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_data.tar.gz -C /data .

# Restore volumes
docker run --rm -v falcon-vision_postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_data.tar.gz -C /data
```

## Scaling

### Horizontal Scaling
```yaml
# Scale services
docker-compose up -d --scale backend=3 --scale frontend=2

# Load balancer configuration
nginx:
  image: nginx
  ports:
    - "80:80"
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf
  depends_on:
    - backend
    - frontend
```

### Resource Limits
```yaml
# Resource constraints
deploy:
  resources:
    limits:
      cpus: '0.5'
      memory: 512M
    reservations:
      cpus: '0.25'
      memory: 256M
```

## Troubleshooting

### Common Issues

#### Port Conflicts
```bash
# Check port usage
netstat -tulpn | grep :8000

# Kill process using port
sudo kill -9 $(lsof -ti:8000)
```

#### Container Won't Start
```bash
# Check logs
docker-compose logs backend

# Check container status
docker-compose ps

# Restart specific service
docker-compose restart backend
```

#### Database Connection Issues
```bash
# Check database logs
docker-compose logs db

# Test database connection
docker-compose exec backend python -c "from app.database import engine; print(engine.connect())"
```

#### Memory Issues
```bash
# Check memory usage
docker stats

# Increase memory limits
docker-compose up -d --scale backend=1
```

### Debug Mode
```bash
# Enable debug mode
DEBUG=true docker-compose up

# Run container in debug mode
docker-compose run --rm backend bash

# Check container environment
docker-compose exec backend env
```

## Security

### Security Best Practices
- Use secrets for sensitive data
- Keep images updated
- Use non-root users
- Enable security scanning
- Use HTTPS in production

### Secrets Management
```yaml
# Use Docker secrets
secrets:
  db_password:
    file: ./secrets/db_password.txt
  jwt_secret:
    file: ./secrets/jwt_secret.txt

services:
  backend:
    secrets:
      - db_password
      - jwt_secret
    environment:
      - DATABASE_PASSWORD_FILE=/run/secrets/db_password
      - JWT_SECRET_FILE=/run/secrets/jwt_secret
```

## Performance Optimization

### Image Optimization
- Use multi-stage builds
- Minimize image layers
- Use .dockerignore
- Optimize base images

### Runtime Optimization
- Use health checks
- Configure resource limits
- Enable logging rotation
- Use volume mounts for data

## Maintenance

### Updates
```bash
# Update images
docker-compose pull
docker-compose up -d

# Update specific service
docker-compose pull backend
docker-compose up -d backend
```

### Cleanup
```bash
# Remove unused containers
docker container prune

# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune

# Complete cleanup
docker system prune -a
```
