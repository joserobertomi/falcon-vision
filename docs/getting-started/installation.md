# Installation

This guide will help you install and set up Falcon Vision on your system.

## Prerequisites

Before installing Falcon Vision, ensure you have the following installed:

- **Docker** (20.10+) and **Docker Compose** (2.0+)
- **Git** for cloning the repository
- **Make** (optional, for convenience scripts)

### System Requirements

- **RAM**: Minimum 4GB, recommended 8GB+
- **CPU**: 2+ cores recommended
- **Storage**: 10GB+ free space
- **OS**: Linux, macOS, or Windows with WSL2

## Installation Methods

### Method 1: Docker Compose (Recommended)

This is the easiest way to get started:

```bash
# Clone the repository
git clone https://github.com/falcon-vision/falcon-vision.git
cd falcon-vision

# Copy environment template
cp .env.example .env

# Edit configuration (optional)
nano .env

# Start all services
docker-compose up -d
```

### Method 2: Development Setup

For development and customization:

```bash
# Clone the repository
git clone https://github.com/falcon-vision/falcon-vision.git
cd falcon-vision

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install

# UI setup
cd ../ui
pip install -r requirements.txt

# Database setup
cd ../backend
alembic upgrade head
```

## Environment Configuration

### Required Environment Variables

Create a `.env` file in the project root with these variables:

```bash
# Database
POSTGRES_PASSWORD=your_secure_password
POSTGRES_USER=postgres
POSTGRES_DB=falcon_vision
POSTGRES_SERVER=db
POSTGRES_PORT=5432

# Security
SECRET_KEY=your_secret_key_here
FIRST_SUPERUSER=admin@example.com
FIRST_SUPERUSER_PASSWORD=admin_password

# Domain (for production)
DOMAIN=yourdomain.com
STACK_NAME=falcon-vision

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000","https://localhost:3000","http://localhost","https://localhost"]
```

### Optional Environment Variables

```bash
# Email (for password recovery)
SMTP_HOST=smtp.gmail.com
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAILS_FROM_EMAIL=noreply@yourdomain.com

# Monitoring
SENTRY_DSN=your_sentry_dsn

# Docker Images
DOCKER_IMAGE_BACKEND=falcon-vision-backend
DOCKER_IMAGE_FRONTEND=falcon-vision-frontend
DOCKER_IMAGE_UI=falcon-vision-ui
TAG=latest
```

## Verification

After installation, verify everything is working:

### 1. Check Services Status

```bash
docker-compose ps
```

All services should show "Up" status.

### 2. Test API Health

```bash
curl http://localhost:8000/api/v1/utils/health-check/
```

Expected response:
```json
{"status": "ok"}
```

### 3. Access Applications

- **Frontend Dashboard**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Analytics UI**: http://localhost:5174
- **Database Admin**: http://localhost:8080

## Troubleshooting

### Common Issues

#### Port Already in Use

If you get port conflicts:

```bash
# Check what's using the port
sudo netstat -tulpn | grep :8000

# Kill the process or change ports in docker-compose.yml
```

#### Database Connection Issues

```bash
# Check database logs
docker-compose logs db

# Restart database
docker-compose restart db
```

#### Permission Issues

```bash
# Fix file permissions
sudo chown -R $USER:$USER .
chmod -R 755 .
```

### Getting Help

If you encounter issues:

1. Check the [troubleshooting section](troubleshooting.md)
2. Review the [GitHub issues](https://github.com/falcon-vision/falcon-vision/issues)
3. Join our community discussions

## Next Steps

Once installation is complete:

1. **[Quick Start Guide](quick-start.md)** - Learn the basics
2. **[Configuration Guide](configuration.md)** - Customize your setup
3. **[Architecture Overview](../architecture/overview.md)** - Understand the system

