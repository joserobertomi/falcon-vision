# Backend Architecture

## Overview

The Falcon Vision backend is built using FastAPI and provides a robust API for person detection, analytics, and real-time video streaming.

## Technology Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLModel ORM
- **Authentication**: JWT tokens
- **Computer Vision**: OpenCV and YOLOv8
- **WebSocket**: Real-time video streaming
- **Migrations**: Alembic

## Core Components

### API Routes

- **Authentication**: User login, registration, and token management
- **Person Detection**: Real-time detection endpoints
- **Analytics**: Detection metrics and statistics
- **WebSocket Streaming**: Live video feed processing

### Database Models

- **User**: User authentication and profile data
- **Detection**: Person detection records and metadata
- **Analytics**: Aggregated statistics and metrics

### Services

- **DetectionService**: Handles YOLOv8 model inference
- **AnalyticsService**: Processes and aggregates detection data
- **AuthService**: Manages user authentication and authorization

## API Structure

```
/api/v1/
├── auth/           # Authentication endpoints
├── detections/     # Person detection endpoints
├── analytics/      # Analytics and metrics
└── streaming/      # WebSocket video streaming
```

## Configuration

The backend uses environment variables for configuration:

- Database connection settings
- JWT secret keys
- Email configuration
- Model parameters

## Security

- JWT-based authentication
- CORS configuration
- Input validation with Pydantic
- SQL injection prevention with SQLModel

## Performance

- Async/await for non-blocking operations
- Database connection pooling
- Efficient model inference with OpenCV
- WebSocket for real-time communication
