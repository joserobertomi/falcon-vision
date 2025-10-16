I'll create a more concise and summarized version of the README. Here's the streamlined version:

```markdown
# 🎨 FALCON Vision UI Service

A Streamlit-based frontend for the FALCON Vision computer vision system, providing real-time camera monitoring and analytics dashboards.

## 🎯 Features

- **📷 Camera Monitoring**: Live webcam feed with person detection and tracking
- **📊 Analytics Dashboard**: Interactive data visualization and insights
- **🤖 LLM Integration**: Natural language querying of detection data
- **👤 User Management**: Authentication and registration

## 🛠️ Tech Stack

- **Streamlit 1.50+** - Web framework
- **Python 3.10+** - Core language
- **Plotly** - Data visualizations
- **Docker** - Containerization
- **uv** - Package management

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Docker & Docker Compose
- Webcam access
- Backend API running (port 8000)

### Installation

1. **Clone repository**
```bash
git clone https://github.com/joserobertomi/falcon-vision.git
cd falcon-vision/ui
```

2. **Run with Docker**
```bash
docker compose up --build
```

3. **Local development**
```bash
uv sync
streamlit run app/main.py --server.port=5174
```

4. **Access application**
- UI Service: `http://localhost:5174`
- Backend API: `http://localhost:8000`

## 📁 Structure

```
ui/
├── app/
│   ├── main.py                 # Main application
│   ├── pages/                  # Application pages
│   │   ├── home.py            # Home
│   │   ├── camera.py          # Camera monitoring
│   │   ├── analytics.py       # Analytics dashboard
│   │   └── signup.py          # User registration
│   └── widgets/               # Reusable components
│       ├── real_demo_analytics.py    # Live analytics
│       └── stored_analytics.py       # Historical analytics
├── Dockerfile
├── pyproject.toml
└── README.md
```

## 📱 Pages

### 🏠 Home
- Project overview and navigation
- System status

### 📷 Camera
- Real-time video capture
- Person detection with bounding boxes
- WebSocket integration
- QR code termination

### 📊 Analytics
- **Real Demo**: Live session analytics
- **Stored Analytics**: Historical data analysis
- Interactive dashboards
- Data filtering and export

### 👤 Signup
- User registration
- Authentication

## ⚙️ Configuration

### Environment Variables
```bash
STREAMLIT_SERVER_PORT=5174
STREAMLIT_SERVER_ADDRESS=0.0.0.0
BACKEND_API_URL=http://localhost:8000
```

## 🐳 Docker

### Build & Run
```bash
docker build -t falcon-vision-ui .
docker run -p 5174:5174 falcon-vision-ui
```

### Docker Compose
```yaml
services:
  ui:
    build: ./ui
    ports:
      - "5174:5174"
    environment:
      - BACKEND_API_URL=http://backend:8000
```

## 🔧 Development

### Adding Pages
1. Create file in `app/pages/`
2. Add to `app/main.py` navigation
3. Follow Streamlit patterns

### API Integration
- Use `requests` for HTTP calls
- Implement error handling
- Cache responses when appropriate

## 🚨 Troubleshooting

**Camera issues**: Check webcam permissions and availability
**Analytics not loading**: Verify backend API is running
**Docker issues**: Check Docker is running and syntax