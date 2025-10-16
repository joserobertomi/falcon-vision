# Installation Guide

## Overview

This guide will help you install and set up Falcon Vision on your system. We provide multiple installation methods to suit different use cases.

## Prerequisites

### System Requirements
- **Operating System**: Linux (Ubuntu 20.04+), macOS (10.15+), or Windows 10+
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 10GB free space minimum
- **CPU**: 2 cores minimum, 4 cores recommended
- **GPU**: Optional but recommended for better performance

### Software Requirements
- **Docker**: 20.10+ with BuildKit support
- **Docker Compose**: 2.0+
- **Git**: 2.30+
- **Node.js**: 18+ (for local development)
- **Python**: 3.10+ (for local development)

## Installation Methods

### Method 1: Docker (Recommended)

#### 1. Clone Repository
```bash
git clone https://github.com/falcon-vision/falcon-vision.git
cd falcon-vision
```

#### 2. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

#### 3. Start Services
```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps
```

#### 4. Verify Installation
```bash
# Test API
curl http://localhost:8000/health

# Test frontend
curl http://localhost:5173

# Test UI dashboard
curl http://localhost:5174
```

### Method 2: Local Development

#### 1. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Set up database
alembic upgrade head

# Start backend server
fastapi run --reload app/main.py
```

#### 2. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

#### 3. UI Dashboard Setup
```bash
# Navigate to UI directory
cd ui

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Start UI server
streamlit run app/main.py
```

### Method 3: Production Deployment

#### 1. Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 2. Application Deployment
```bash
# Clone repository
git clone https://github.com/falcon-vision/falcon-vision.git
cd falcon-vision

# Configure environment
cp .env.example .env.production
nano .env.production

# Start services
docker-compose -f docker-compose.prod.yml up -d
```

## Configuration

### Environment Variables

#### Backend Configuration
```bash
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/falcon_vision

# JWT
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]

# Email
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_TLS=false
EMAILS_FROM_EMAIL=noreply@example.com
```

#### Frontend Configuration
```bash
# API Configuration
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000

# Environment
NODE_ENV=development
VITE_DEBUG=true
```

### Database Setup

#### PostgreSQL Installation
```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Create database
sudo -u postgres psql
CREATE DATABASE falcon_vision;
CREATE USER falcon_user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE falcon_vision TO falcon_user;
\q
```

#### Database Migration
```bash
# Run migrations
alembic upgrade head

# Create initial data (optional)
python scripts/create_initial_data.py
```

## Verification

### Health Checks

#### Backend Health
```bash
# Check API health
curl http://localhost:8000/health

# Expected response
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0"
}
```

#### Frontend Health
```bash
# Check frontend
curl http://localhost:5173

# Should return HTML content
```

#### Database Health
```bash
# Check database connection
docker-compose exec db pg_isready -U postgres

# Expected response
postgresql://postgres@localhost:5432/falcon_vision - accepting connections
```

### API Testing

#### Authentication Test
```bash
# Register user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123","full_name":"Test User"}'

# Login user
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=testpass123"
```

#### Detection Test
```bash
# Test person detection (with auth token)
curl -X POST http://localhost:8000/api/v1/detections/person \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "image=@test_image.jpg"
```

## Troubleshooting

### Common Issues

#### Docker Issues
```bash
# Check Docker status
docker --version
docker-compose --version

# Check running containers
docker ps

# Check logs
docker-compose logs backend
docker-compose logs frontend
```

#### Port Conflicts
```bash
# Check port usage
netstat -tulpn | grep :8000
netstat -tulpn | grep :5173

# Kill process using port
sudo kill -9 $(lsof -ti:8000)
```

#### Database Issues
```bash
# Check database status
docker-compose exec db pg_isready -U postgres

# Check database logs
docker-compose logs db

# Reset database
docker-compose down -v
docker-compose up -d
```

#### Permission Issues
```bash
# Fix Docker permissions
sudo usermod -aG docker $USER
newgrp docker

# Fix file permissions
sudo chown -R $USER:$USER .
```

### Debug Mode

#### Backend Debug
```bash
# Enable debug logging
export DEBUG=true
export LOG_LEVEL=DEBUG

# Start with debugger
python -m debugpy --listen 5678 --wait-for-client app/main.py
```

#### Frontend Debug
```bash
# Enable debug mode
export VITE_DEBUG=true
export VITE_LOG_LEVEL=debug

# Start with debugger
npm run dev -- --inspect
```

## Performance Optimization

### Docker Optimization
```bash
# Increase memory limits
docker-compose up -d --scale backend=2

# Use production images
docker-compose -f docker-compose.prod.yml up -d
```

### Database Optimization
```sql
-- Create indexes
CREATE INDEX idx_detections_timestamp ON detections(timestamp);
CREATE INDEX idx_detections_user_id ON detections(user_id);
CREATE INDEX idx_users_email ON users(email);
```

### Application Optimization
```bash
# Enable GPU support (if available)
export CUDA_VISIBLE_DEVICES=0

# Increase worker processes
export WORKERS=4
```

## Security Setup

### SSL/TLS Configuration
```bash
# Install Certbot
sudo apt install certbot

# Obtain SSL certificate
sudo certbot certonly --standalone -d your-domain.com

# Configure Nginx with SSL
sudo nano /etc/nginx/sites-available/falcon-vision
```

### Firewall Configuration
```bash
# Configure UFW
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### Environment Security
```bash
# Secure environment file
chmod 600 .env
chown $USER:$USER .env

# Use strong passwords
openssl rand -base64 32
```

## Maintenance

### Updates
```bash
# Update application
git pull origin main
docker-compose pull
docker-compose up -d

# Update dependencies
pip install -r requirements.txt --upgrade
npm update
```

### Backups
```bash
# Backup database
docker-compose exec db pg_dump -U postgres falcon_vision > backup.sql

# Backup application
tar -czf falcon-vision-backup.tar.gz .
```

### Monitoring
```bash
# Check service status
docker-compose ps

# Monitor logs
docker-compose logs -f

# Check resource usage
docker stats
```

## Next Steps

After successful installation:

1. **Configure Authentication**: Set up user accounts and permissions
2. **Upload Test Data**: Add sample images for testing
3. **Configure Detection**: Adjust model parameters
4. **Set Up Monitoring**: Configure logging and metrics
5. **Deploy to Production**: Follow production deployment guide

## Support

If you encounter issues during installation:

1. Check the troubleshooting section above
2. Review the logs for error messages
3. Search existing issues on GitHub
4. Create a new issue with detailed information
5. Join our community Discord for help

## Additional Resources

- [Quick Start Guide](quick-start.md)
- [Configuration Guide](configuration.md)
- [Development Setup](../development/setup.md)
- [Production Deployment](../deployment/production.md)
- [API Documentation](../api/authentication.md)