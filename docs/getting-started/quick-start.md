# Quick Start Guide

## Overview

Get Falcon Vision up and running in 5 minutes! This guide provides the fastest way to start using Falcon Vision for person detection and analytics.

## Prerequisites

- **Docker** and **Docker Compose** installed
- **Git** for cloning the repository
- **4GB RAM** minimum
- **Web browser** for accessing the interface

## Quick Installation

### 1. Clone and Start
```bash
# Clone the repository
git clone https://github.com/falcon-vision/falcon-vision.git
cd falcon-vision

# Start all services
docker-compose up -d
```

### 2. Wait for Services
```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### 3. Access the Application
- **Frontend Dashboard**: http://localhost:5173
- **API Documentation**: http://localhost:8000/docs
- **UI Analytics**: http://localhost:5174
- **Documentation**: http://localhost:8001

## First Steps

### 1. Create User Account
1. Open http://localhost:5173 in your browser
2. Click "Register" to create a new account
3. Fill in your details and click "Register"
4. You'll be automatically logged in

### 2. Test Person Detection
1. Go to the "Detection" page
2. Click "Start Camera" to enable your webcam
3. Allow camera access when prompted
4. You should see real-time person detection overlays

### 3. View Analytics
1. Go to the "Analytics" page
2. View detection statistics and charts
3. Explore different time periods and filters

## Quick Configuration

### Basic Settings
```bash
# Edit environment variables
nano .env

# Key settings to configure:
# - JWT_SECRET_KEY: Your secret key for authentication
# - DATABASE_URL: Database connection string
# - CORS_ORIGINS: Allowed frontend origins
```

### Detection Parameters
```bash
# Adjust detection sensitivity
CONFIDENCE_THRESHOLD=0.5  # Lower = more detections, higher = more accurate
NMS_THRESHOLD=0.45        # Non-maximum suppression threshold
MAX_DETECTIONS=100        # Maximum detections per frame
```

## Testing the Installation

### 1. API Health Check
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0"
}
```

### 2. Authentication Test
```bash
# Register a test user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123","full_name":"Test User"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=testpass123"
```

### 3. Detection Test
```bash
# Test detection with a sample image
curl -X POST http://localhost:8000/api/v1/detections/person \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "image=@sample_image.jpg"
```

## Common Issues

### Services Won't Start
```bash
# Check Docker status
docker --version
docker-compose --version

# Check port conflicts
netstat -tulpn | grep :8000
netstat -tulpn | grep :5173

# Restart services
docker-compose down
docker-compose up -d
```

### Camera Not Working
1. Ensure camera permissions are granted
2. Check if camera is being used by another application
3. Try refreshing the page
4. Check browser console for errors

### Database Issues
```bash
# Check database status
docker-compose exec db pg_isready -U postgres

# Reset database
docker-compose down -v
docker-compose up -d
```

## Next Steps

### 1. Explore Features
- **Real-time Detection**: Use the camera for live person detection
- **Analytics Dashboard**: View detection statistics and trends
- **User Management**: Manage user accounts and permissions
- **API Integration**: Use the REST API for custom integrations

### 2. Configuration
- **Detection Settings**: Adjust confidence thresholds and parameters
- **User Roles**: Set up different user permission levels
- **Email Notifications**: Configure SMTP for email alerts
- **Database**: Set up external PostgreSQL for production

### 3. Development
- **API Documentation**: Explore the interactive API docs
- **WebSocket Streaming**: Implement real-time video streaming
- **Custom Models**: Integrate your own detection models
- **Frontend Customization**: Modify the React frontend

## Production Deployment

### Quick Production Setup
```bash
# Use production configuration
docker-compose -f docker-compose.prod.yml up -d

# Set up SSL certificates
sudo certbot --nginx -d your-domain.com

# Configure reverse proxy
sudo nano /etc/nginx/sites-available/falcon-vision
```

### Environment Variables
```bash
# Production environment
DEBUG=false
LOG_LEVEL=INFO
DATABASE_URL=postgresql://user:pass@db.example.com:5432/falcon_vision
JWT_SECRET_KEY=your-super-secret-production-key
CORS_ORIGINS=["https://your-domain.com"]
```

## Performance Tips

### For Better Performance
1. **Use GPU**: Enable CUDA for faster detection
2. **Increase Memory**: Allocate more RAM to Docker
3. **Optimize Images**: Use smaller image sizes for faster processing
4. **Database Indexing**: Add indexes for better query performance

### Resource Requirements
- **Minimum**: 4GB RAM, 2 CPU cores
- **Recommended**: 8GB RAM, 4 CPU cores
- **GPU**: Optional but recommended for real-time processing

## Troubleshooting

### Check Logs
```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db
```

### Common Solutions
1. **Port Conflicts**: Change ports in docker-compose.yml
2. **Permission Issues**: Fix Docker permissions
3. **Memory Issues**: Increase Docker memory limits
4. **Network Issues**: Check firewall settings

### Debug Mode
```bash
# Enable debug logging
export DEBUG=true
export LOG_LEVEL=DEBUG

# Restart services
docker-compose restart
```

## Support

### Getting Help
1. **Documentation**: Check the full documentation
2. **GitHub Issues**: Search existing issues
3. **Community**: Join our Discord server
4. **Email**: Contact support@falcon-vision.com

### Useful Links
- **GitHub Repository**: https://github.com/falcon-vision/falcon-vision
- **Documentation**: https://docs.falcon-vision.com
- **API Reference**: http://localhost:8000/docs
- **Community Discord**: https://discord.gg/falcon-vision

## What's Next?

Now that you have Falcon Vision running:

1. **Read the Full Documentation**: Explore all features and capabilities
2. **Configure for Production**: Set up proper security and monitoring
3. **Integrate with Your System**: Use the API for custom integrations
4. **Contribute**: Help improve Falcon Vision by contributing code
5. **Share**: Tell others about Falcon Vision

## Quick Reference

### Essential Commands
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Update services
docker-compose pull
docker-compose up -d
```

### Key URLs
- Frontend: http://localhost:5173
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- UI Dashboard: http://localhost:5174
- Documentation: http://localhost:8001

### Important Files
- `.env`: Environment configuration
- `docker-compose.yml`: Service configuration
- `backend/app/main.py`: Backend application
- `frontend/src/`: Frontend source code
- `ui/app/`: UI dashboard source code