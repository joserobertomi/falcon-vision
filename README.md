# 🧠 FALCON Vision

A real-time computer vision application for person detection, tracking, and intelligent analytics with LLM integration.

## 🎯 Project Overview

FALCON Vision is a computer vision system that detects and tracks people in real-time, records their characteristics and movements, and provides an interactive analytics dashboard with LLM-powered querying capabilities.

## 🏗️ System Architecture

### Application Flow
```
FE-Camera <--> (WebSocket) <--> BE-CV (ML) <--> DB <--> BE(API/LLM) <--> FE-Analytics
```

### Specific Flows
- **Capture & Streaming**: `FE-Camera → BE-CV`
- **Inference & Recording**: `BE-CV → DB`
- **Query & Display**: `FE-Analytics ← BE(cv-API/LLM) ← DB`
- **LLM Prompts**: `FE-Analytics ↔ BE-LLM`

## 🎮 Frontend Pages

### Page 1: Computer Vision (CV)
- **Real-time Camera Capture**: Capture images and support WebSocket connection for streaming data to backend
- **Live Detection Display**: Show real-time detections with bounding boxes and status information
- **WebSocket Integration**: Stream data to backend for processing

### Page 2: Analytics
- **Mode 1 - Dashboard**: Create dashboards and visualization tools for database data via HTTP API
- **Mode 2 - LLM Interaction**: Interactive chat interface with LLM for intelligent data querying (Final Stage)

## ⚙️ Backend - Computer Vision

### 1. Data Collection & Model Training
- **Person Detection**: Use pre-trained models (YOLO, MediaPipe, or custom models)
- **Database Integration**: Create records for each status change detected by camera
- **QR Code Termination**: Stop operation when specific QR code is detected

### 2. WebSocket Implementation
- **Asynchronous Streaming**: Build WebSocket routes for real-time video streaming
- **Performance Optimization**: Avoid API latency issues similar to autonomous vehicle project

### 3. API Development
- **Analytics Data Routes**: Build routes for analytics dashboard data retrieval
- **Polygon Management**: Create API routes for polygon definition and management

### 4. LLM Integration (Final Stage)
- **Database Queries**: Query database based on user prompts
- **Input**: Natural language prompts for information retrieval
- **Output**: Intelligent responses based on detection data


## 🚀 Incremental Features

- **Polygon Construction**: Build tools for creating ROIs (Regions of Interest)
- **State-based Recording**: Record based on state changes to avoid duplicate instances
- **Advanced Tracking**: Implement person re-identification and tracking
- **Real-time Processing**: Efficient data processing and storage

## 🛠️ Technology Stack

### Backend
- **Python** for main development
- **FastAPI** for API development
- **WebSocket** for real-time communication
- **PostgreSQL** for data storage
- **Computer Vision**: YOLO, MediaPipe, OpenCV
- **AI/ML**: PyTorch, Transformers

### Frontend
- **React** with TypeScript
- **Chakra UI** for components
- **WebSocket Client** for real-time data
- **Analytics Dashboard** with custom visualizations

### AI Integration
- **LLM Integration**: OpenAI, Gemini, or local models
- **Natural Language Processing** for query understanding
- **Intelligent Data Interpretation**

## 🎯 Key Features

### Real-time Detection
- **Person Detection**: Identify and track people in video streams
- **Status Monitoring**: Track movement, object interaction, and EPI detection
- **Visual Characteristics**: Record colors and other visual features

### Analytics Dashboard
- **Data Visualization**: Innovative charts and graphs (no basic pie charts!)
- **Historical Analysis**: Time-based filtering and data exploration
- **Interactive Queries**: Natural language data exploration

### ROI Management
- **Polygon Definition**: Interactive tools for creating regions of interest
- **Area Monitoring**: Track detections within specific regions
- **Spatial Analytics**: Analyze movement patterns within defined areas

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Docker & Docker Compose
- Webcam access

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/joserobertomi/falcon-vision.git
cd falcon-vision
```

2. **Run with Docker**
```bash
docker compose up --build
```

3. **Access the application**
- Main app: `http://localhost:5174`
- API docs: `http://localhost:8000/docs`

## 📚 Documentation

- **Project Notes**: [docs/notes.md](./docs/notes.md)
- **Development Guide**: [development.md](./development.md)
- **Deployment Guide**: [deployment.md](./deployment.md)

## 🎯 Development Phases

### Phase 1: Core CV System
- [ x ] Implement person detection with YOLO
- [ x ] Build WebSocket streaming infrastructure
- [ x ] Create database schema and models
- [ x ] Develop basic frontend camera interface

### Phase 2: Analytics Dashboard
- [ x ] Build analytics visualization components
- [ x ] Implement data filtering and search
- [] Create polygon management tools
- [] Add state-based recording system

### Phase 3: LLM Integration
- [] Integrate LLM API (OpenAI/Gemini)
- [] Build natural language query system
- [] Implement intelligent data interpretation
- [] Add conversational interface
