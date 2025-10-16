# Quick Start

Get Falcon Vision running in 5 minutes with this quick start guide.

## Prerequisites

- Docker and Docker Compose installed
- Git installed
- 4GB+ RAM available

## Step 1: Clone and Start

```bash
# Clone the repository
git clone https://github.com/falcon-vision/falcon-vision.git
cd falcon-vision

# Start all services
docker-compose up -d
```

## Step 2: Wait for Services

Wait about 2-3 minutes for all services to start up. You can monitor progress:

```bash
# Watch logs
docker-compose logs -f

# Check service status
docker-compose ps
```

## Step 3: Access Applications

Once all services are running, access:

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend Dashboard** | http://localhost:3000 | Main user interface |
| **API Documentation** | http://localhost:8000/docs | Interactive API docs |
| **Analytics UI** | http://localhost:5174 | Streamlit analytics dashboard |
| **Database Admin** | http://localhost:8080 | PostgreSQL admin interface |

## Step 4: First Login

1. Open http://localhost:3000
2. Click "Sign Up" to create an account
3. Or use the default admin credentials:
   - **Email**: `admin@example.com`
   - **Password**: `changethis`

!!! warning "Change Default Credentials"
    Make sure to change the default admin password in production!

## Step 5: Test Video Streaming

1. Go to the **Analytics UI** at http://localhost:5174
2. Click on "Camera" tab
3. Start video streaming to test person detection
4. View real-time analytics in the dashboard

## What's Running?

Your Falcon Vision instance includes:

- **Backend API** (FastAPI) - Core application logic
- **Frontend** (React) - User dashboard
- **UI Dashboard** (Streamlit) - Analytics interface
- **Database** (PostgreSQL) - Data storage
- **Computer Vision** - Person detection models

## Next Steps

Now that you have Falcon Vision running:

### Explore the Features

- **Person Detection**: Test real-time video analysis
- **Analytics**: View detection metrics and charts
- **User Management**: Create and manage user accounts
- **API Integration**: Use the REST API for custom integrations

### Customize Your Setup

- **[Configuration Guide](configuration.md)** - Customize settings
- **[Environment Variables](configuration.md#environment-variables)** - Configure behavior
- **[API Documentation](../api/authentication.md)** - Integrate with APIs

### Learn More

- **[Architecture Overview](../architecture/overview.md)** - Understand the system
- **[Development Guide](../development/setup.md)** - Start developing
- **[Deployment Guide](../deployment/docker.md)** - Deploy to production

## Troubleshooting

### Services Won't Start

```bash
# Check logs for errors
docker-compose logs

# Restart services
docker-compose restart

# Rebuild if needed
docker-compose up --build -d
```

### Can't Access Applications

1. **Check if ports are available**:
   ```bash
   netstat -tulpn | grep -E ':(3000|8000|5174|8080)'
   ```

2. **Verify Docker is running**:
   ```bash
   docker --version
   docker-compose --version
   ```

3. **Check firewall settings** (if applicable)

### Performance Issues

- Ensure you have at least 4GB RAM available
- Close other resource-intensive applications
- Consider using SSD storage for better performance

## Getting Help

- **Documentation**: Browse the full documentation
- **GitHub Issues**: [Report problems](https://github.com/falcon-vision/falcon-vision/issues)
- **Community**: Join discussions on GitHub

---

🎉 **Congratulations!** You now have Falcon Vision running locally. Explore the features and start building amazing computer vision applications!

