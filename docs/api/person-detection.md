# Person Detection API

## Overview

The Person Detection API provides endpoints for real-time person detection using YOLOv8, detection history, and analytics.

## Detection Endpoints

### POST /api/v1/detections/person
Process a single image for person detection.

**Headers:**
- `Authorization: Bearer <access_token>`
- `Content-Type: multipart/form-data`

**Request Body:**
- `image` (file, required): Image file (JPEG, PNG, WebP)
- `confidence_threshold` (float, optional): Detection confidence threshold (default: 0.5)

**Response:**
```json
{
  "detections": [
    {
      "id": "detection-uuid",
      "bbox": {
        "x1": 100,
        "y1": 150,
        "x2": 300,
        "y2": 400,
        "width": 200,
        "height": 250
      },
      "confidence": 0.95,
      "class_id": 0,
      "class_name": "person",
      "timestamp": "2024-01-01T12:00:00Z"
    }
  ],
  "image_info": {
    "width": 640,
    "height": 480,
    "format": "JPEG"
  },
  "processing_time": 0.15,
  "total_detections": 1
}
```

### GET /api/v1/detections/person
Get detection history with filtering and pagination.

**Headers:**
- `Authorization: Bearer <access_token>`

**Query Parameters:**
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum number of records (default: 100)
- `start_date` (string, optional): Start date filter (ISO format)
- `end_date` (string, optional): End date filter (ISO format)
- `min_confidence` (float, optional): Minimum confidence threshold
- `user_id` (string, optional): Filter by user ID (admin only)

**Response:**
```json
{
  "detections": [
    {
      "id": "detection-uuid",
      "user_id": "user-uuid",
      "bbox": {
        "x1": 100,
        "y1": 150,
        "x2": 300,
        "y2": 400,
        "width": 200,
        "height": 250
      },
      "confidence": 0.95,
      "class_id": 0,
      "class_name": "person",
      "timestamp": "2024-01-01T12:00:00Z",
      "image_path": "/images/detection-uuid.jpg"
    }
  ],
  "total": 150,
  "skip": 0,
  "limit": 100
}
```

### GET /api/v1/detections/person/{detection_id}
Get specific detection details.

**Headers:**
- `Authorization: Bearer <access_token>`

**Path Parameters:**
- `detection_id` (string, required): Detection UUID

**Response:**
```json
{
  "id": "detection-uuid",
  "user_id": "user-uuid",
  "bbox": {
    "x1": 100,
    "y1": 150,
    "x2": 300,
    "y2": 400,
    "width": 200,
    "height": 250
  },
  "confidence": 0.95,
  "class_id": 0,
  "class_name": "person",
  "timestamp": "2024-01-01T12:00:00Z",
  "image_path": "/images/detection-uuid.jpg",
  "processing_time": 0.15,
  "model_version": "yolov8n-v1.0"
}
```

### DELETE /api/v1/detections/person/{detection_id}
Delete a detection record.

**Headers:**
- `Authorization: Bearer <access_token>`

**Path Parameters:**
- `detection_id` (string, required): Detection UUID

**Response:**
- `204 No Content`: Detection deleted successfully
- `404 Not Found`: Detection not found
- `403 Forbidden`: Insufficient permissions

## Batch Processing

### POST /api/v1/detections/person/batch
Process multiple images for person detection.

**Headers:**
- `Authorization: Bearer <access_token>`
- `Content-Type: multipart/form-data`

**Request Body:**
- `images` (files, required): Multiple image files
- `confidence_threshold` (float, optional): Detection confidence threshold

**Response:**
```json
{
  "results": [
    {
      "image_name": "image1.jpg",
      "detections": [
        {
          "bbox": {
            "x1": 100,
            "y1": 150,
            "x2": 300,
            "y2": 400,
            "width": 200,
            "height": 250
          },
          "confidence": 0.95,
          "class_id": 0,
          "class_name": "person"
        }
      ],
      "total_detections": 1,
      "processing_time": 0.15
    }
  ],
  "total_images": 1,
  "total_detections": 1,
  "total_processing_time": 0.15
}
```

## Detection Statistics

### GET /api/v1/detections/person/stats
Get detection statistics and metrics.

**Headers:**
- `Authorization: Bearer <access_token>`

**Query Parameters:**
- `start_date` (string, optional): Start date filter (ISO format)
- `end_date` (string, optional): End date filter (ISO format)
- `group_by` (string, optional): Group by period (hour, day, week, month)

**Response:**
```json
{
  "summary": {
    "total_detections": 1250,
    "unique_persons": 45,
    "average_confidence": 0.87,
    "detection_rate": 0.75
  },
  "time_series": [
    {
      "timestamp": "2024-01-01T00:00:00Z",
      "detections": 15,
      "unique_persons": 3,
      "average_confidence": 0.89
    }
  ],
  "confidence_distribution": {
    "0.9-1.0": 450,
    "0.8-0.9": 600,
    "0.7-0.8": 150,
    "0.6-0.7": 50
  },
  "hourly_distribution": {
    "00": 25,
    "01": 15,
    "02": 10,
    "12": 85,
    "13": 95
  }
}
```

## Model Configuration

### GET /api/v1/detections/model/config
Get current model configuration.

**Headers:**
- `Authorization: Bearer <access_token>`

**Response:**
```json
{
  "model_name": "yolov8n",
  "version": "1.0",
  "input_size": [640, 640],
  "confidence_threshold": 0.5,
  "nms_threshold": 0.45,
  "max_detections": 100,
  "classes": [
    {
      "id": 0,
      "name": "person"
    }
  ],
  "performance": {
    "average_inference_time": 0.15,
    "fps": 6.67,
    "memory_usage": "2.1GB"
  }
}
```

### PUT /api/v1/detections/model/config
Update model configuration (admin only).

**Headers:**
- `Authorization: Bearer <access_token>`
- `Content-Type: application/json`

**Request Body:**
```json
{
  "confidence_threshold": 0.6,
  "nms_threshold": 0.5,
  "max_detections": 150
}
```

**Response:**
```json
{
  "message": "Model configuration updated successfully",
  "new_config": {
    "confidence_threshold": 0.6,
    "nms_threshold": 0.5,
    "max_detections": 150
  }
}
```

## Error Handling

### Common Error Responses

#### 400 Bad Request
```json
{
  "detail": "Invalid image format. Supported formats: JPEG, PNG, WebP"
}
```

#### 413 Payload Too Large
```json
{
  "detail": "Image file too large. Maximum size: 10MB"
}
```

#### 422 Unprocessable Entity
```json
{
  "detail": "Invalid confidence threshold. Must be between 0.0 and 1.0"
}
```

#### 500 Internal Server Error
```json
{
  "detail": "Model inference failed",
  "error_code": "MODEL_ERROR"
}
```

## Rate Limiting

### Detection Requests
- **Rate Limit**: 10 requests per minute per user
- **Burst Limit**: 2 requests per second
- **Batch Processing**: 5 images per batch request

### File Upload Limits
- **Max File Size**: 10MB per image
- **Max Batch Size**: 50 images
- **Supported Formats**: JPEG, PNG, WebP

## WebSocket Integration

### Real-time Detection
The detection API integrates with WebSocket streaming for real-time video processing:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/video-stream');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'detection') {
    console.log('Person detected:', data.detection);
  }
};
```

## Testing

### Test Detection
```bash
# Single image detection
curl -X POST http://localhost:8000/api/v1/detections/person \
  -H "Authorization: Bearer <access_token>" \
  -F "image=@test_image.jpg" \
  -F "confidence_threshold=0.5"

# Get detection history
curl -X GET "http://localhost:8000/api/v1/detections/person?limit=10" \
  -H "Authorization: Bearer <access_token>"

# Get statistics
curl -X GET "http://localhost:8000/api/v1/detections/person/stats" \
  -H "Authorization: Bearer <access_token>"
```
