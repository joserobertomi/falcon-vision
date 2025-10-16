# Configuration

Learn how to configure Falcon Vision for your specific needs.

## Environment Variables

Falcon Vision uses environment variables for configuration. Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env

# Edit with your settings
nano .env
```

## Core Configuration

### Database Settings

```bash
# PostgreSQL Configuration
POSTGRES_PASSWORD=your_secure_password
POSTGRES_USER=postgres
POSTGRES_DB=falcon_vision
POSTGRES_SERVER=db
POSTGRES_PORT=5432
```

### Security Settings

```bash
# JWT Secret Key (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
SECRET_KEY=your_secret_key_here

# First Superuser
FIRST_SUPERUSER=admin@example.com
FIRST_SUPERUSER_PASSWORD=secure_admin_password
```

### Domain and CORS

```bash
# Domain (for production)
DOMAIN=yourdomain.com
STACK_NAME=falcon-vision

# CORS Origins (comma-separated)
BACKEND_CORS_ORIGINS=["http://localhost:3000","https://localhost:3000","http://localhost","https://localhost"]
```

## Computer Vision Configuration

### Detection Settings

Configure person detection parameters in the backend:

```python
# In backend/app/cv_model/frame_processor.py
DETECTION_CONFIDENCE = 0.5  # Minimum confidence threshold
DETECTION_IOU_THRESHOLD = 0.45  # IoU threshold for NMS
MAX_DETECTIONS = 100  # Maximum number of detections per frame
```

### Model Configuration

```bash
# YOLO Model Path
YOLO_MODEL_PATH=./yolov8n.pt

# Model Input Size
MODEL_INPUT_SIZE=640
```

## Email Configuration

For password recovery and notifications:

```bash
# SMTP Settings
SMTP_HOST=smtp.gmail.com
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAILS_FROM_EMAIL=noreply@yourdomain.com

# Email Templates
EMAIL_TEMPLATES_DIR=./app/email-templates/build
```

### Gmail Setup

For Gmail SMTP:

1. Enable 2-factor authentication
2. Generate an App Password
3. Use the App Password in `SMTP_PASSWORD`

## Monitoring and Logging

### Sentry Integration

```bash
# Sentry DSN for error tracking
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

### Logging Level

```bash
# Logging configuration
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## Docker Configuration

### Image Names

```bash
# Docker image names
DOCKER_IMAGE_BACKEND=falcon-vision-backend
DOCKER_IMAGE_FRONTEND=falcon-vision-frontend
DOCKER_IMAGE_UI=falcon-vision-ui
TAG=latest
```

### Resource Limits

Modify `docker-compose.yml` to set resource limits:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
```

## Frontend Configuration

### API Endpoints

The frontend automatically detects the API URL based on the environment:

- **Development**: `http://localhost:8000`
- **Production**: `https://api.yourdomain.com`

### Theme Configuration

Customize the UI theme in `frontend/src/theme.tsx`:

```typescript
export const theme = {
  colors: {
    primary: '#3182ce',
    secondary: '#805ad5',
    // ... other colors
  },
  // ... other theme properties
}
```

## Production Configuration

### SSL/TLS

For production deployment with Traefik:

```bash
# Domain configuration
DOMAIN=yourdomain.com
STACK_NAME=falcon-vision

# Traefik labels are automatically configured
```

### Security Headers

Add security headers in `nginx.conf`:

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

### Database Optimization

For production PostgreSQL:

```bash
# In docker-compose.yml, add PostgreSQL configuration
services:
  db:
    environment:
      - POSTGRES_SHARED_BUFFERS=256MB
      - POSTGRES_EFFECTIVE_CACHE_SIZE=1GB
      - POSTGRES_MAINTENANCE_WORK_MEM=64MB
```

## Environment-Specific Configs

### Development

```bash
# .env.development
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
```

### Staging

```bash
# .env.staging
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO
```

### Production

```bash
# .env.production
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
```

## Configuration Validation

### Check Configuration

```bash
# Validate environment variables
docker-compose config

# Test database connection
docker-compose exec backend python -c "from app.core.db import engine; print('DB OK')"

# Test API health
curl http://localhost:8000/api/v1/utils/health-check/
```

### Common Configuration Issues

1. **CORS Errors**: Ensure `BACKEND_CORS_ORIGINS` includes your frontend URL
2. **Database Connection**: Verify `POSTGRES_*` variables match your database
3. **Email Issues**: Check SMTP credentials and firewall settings
4. **SSL Problems**: Ensure domain is properly configured for Traefik

## Advanced Configuration

### Custom Middleware

Add custom middleware in `backend/app/api/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add custom middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Custom Routes

Add custom API routes in `backend/app/api/routes/`:

```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/custom-endpoint")
async def custom_endpoint():
    return {"message": "Custom endpoint"}
```

## Configuration Management

### Using Multiple Environments

```bash
# Use different .env files
docker-compose --env-file .env.development up
docker-compose --env-file .env.production up
```

### Secrets Management

For production, consider using:

- **Docker Secrets**
- **HashiCorp Vault**
- **AWS Secrets Manager**
- **Azure Key Vault**

## Next Steps

- **[Deployment Guide](../deployment/docker.md)** - Deploy your configured application
- **[API Reference](../api/authentication.md)** - Learn about available APIs
- **[Development Guide](../development/setup.md)** - Start customizing the code

