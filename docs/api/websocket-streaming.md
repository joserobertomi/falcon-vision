# WebSocket Streaming API

Real-time video streaming and person detection via WebSocket connections.

## Overview

The WebSocket API provides real-time communication for video streaming and person detection. It's designed for low-latency, bidirectional communication between clients and the server.

## Connection

### WebSocket Endpoint

```
ws://localhost:8000/ws/video-stream
```

For production with SSL:
```
wss://api.yourdomain.com/ws/video-stream
```

### Connection Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `token` | string | Yes | JWT authentication token |
| `client_id` | string | No | Unique client identifier |

### Example Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/video-stream?token=your_jwt_token&client_id=client_123');
```

## Message Format

All messages use JSON format with the following structure:

```json
{
  "type": "message_type",
  "data": { ... },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## Client to Server Messages

### 1. Start Video Stream

Start video streaming with detection.

```json
{
  "type": "start_stream",
  "data": {
    "stream_id": "unique_stream_id",
    "config": {
      "confidence_threshold": 0.5,
      "max_detections": 100,
      "detection_classes": ["person"]
    }
  }
}
```

**Response:**
```json
{
  "type": "stream_started",
  "data": {
    "stream_id": "unique_stream_id",
    "status": "success"
  }
}
```

### 2. Send Video Frame

Send video frame data for processing.

```json
{
  "type": "video_frame",
  "data": {
    "stream_id": "unique_stream_id",
    "frame_data": "base64_encoded_image",
    "frame_number": 123,
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

### 3. Update Stream Configuration

Update detection parameters during streaming.

```json
{
  "type": "update_config",
  "data": {
    "stream_id": "unique_stream_id",
    "config": {
      "confidence_threshold": 0.7,
      "max_detections": 50
    }
  }
}
```

### 4. Stop Video Stream

Stop the video stream.

```json
{
  "type": "stop_stream",
  "data": {
    "stream_id": "unique_stream_id"
  }
}
```

## Server to Client Messages

### 1. Detection Results

Real-time person detection results.

```json
{
  "type": "detection_results",
  "data": {
    "stream_id": "unique_stream_id",
    "frame_number": 123,
    "detections": [
      {
        "class_id": 0,
        "class_name": "person",
        "confidence": 0.85,
        "bbox": {
          "x": 100,
          "y": 150,
          "width": 80,
          "height": 200
        }
      }
    ],
    "processing_time_ms": 45,
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

### 2. Stream Status

Stream status updates.

```json
{
  "type": "stream_status",
  "data": {
    "stream_id": "unique_stream_id",
    "status": "active",
    "fps": 30,
    "total_frames": 1500,
    "detections_count": 45
  }
}
```

### 3. Error Messages

Error notifications.

```json
{
  "type": "error",
  "data": {
    "stream_id": "unique_stream_id",
    "error_code": "INVALID_FRAME",
    "message": "Invalid frame format",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

### 4. Stream Stopped

Confirmation of stream stop.

```json
{
  "type": "stream_stopped",
  "data": {
    "stream_id": "unique_stream_id",
    "total_frames_processed": 1500,
    "total_detections": 45,
    "average_fps": 29.8
  }
}
```

## Error Codes

| Code | Description | Action |
|------|-------------|--------|
| `INVALID_TOKEN` | Invalid or expired JWT token | Re-authenticate |
| `INVALID_FRAME` | Invalid frame format | Check frame encoding |
| `STREAM_NOT_FOUND` | Stream ID not found | Create new stream |
| `DETECTION_FAILED` | Detection processing failed | Retry or check config |
| `RATE_LIMIT_EXCEEDED` | Too many requests | Wait and retry |

## Configuration Options

### Detection Configuration

```json
{
  "confidence_threshold": 0.5,     // Minimum confidence (0.0-1.0)
  "max_detections": 100,           // Maximum detections per frame
  "detection_classes": ["person"], // Classes to detect
  "iou_threshold": 0.45,           // IoU threshold for NMS
  "input_size": 640                // Model input size
}
```

### Stream Configuration

```json
{
  "max_fps": 30,                   // Maximum processing FPS
  "buffer_size": 10,               // Frame buffer size
  "timeout_seconds": 30,           // Stream timeout
  "enable_analytics": true         // Enable analytics tracking
}
```

## Client Implementation Examples

### JavaScript/TypeScript

```typescript
class VideoStreamClient {
  private ws: WebSocket;
  private streamId: string;

  constructor(token: string, clientId?: string) {
    const url = `ws://localhost:8000/ws/video-stream?token=${token}&client_id=${clientId}`;
    this.ws = new WebSocket(url);
    this.setupEventHandlers();
  }

  startStream(config: StreamConfig) {
    this.streamId = `stream_${Date.now()}`;
    this.send({
      type: 'start_stream',
      data: {
        stream_id: this.streamId,
        config
      }
    });
  }

  sendFrame(frameData: string, frameNumber: number) {
    this.send({
      type: 'video_frame',
      data: {
        stream_id: this.streamId,
        frame_data: frameData,
        frame_number: frameNumber,
        timestamp: new Date().toISOString()
      }
    });
  }

  private send(message: any) {
    if (this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }

  private setupEventHandlers() {
    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleMessage(message);
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  private handleMessage(message: any) {
    switch (message.type) {
      case 'detection_results':
        this.onDetectionResults(message.data);
        break;
      case 'stream_status':
        this.onStreamStatus(message.data);
        break;
      case 'error':
        this.onError(message.data);
        break;
    }
  }

  onDetectionResults(data: any) {
    // Handle detection results
    console.log('Detections:', data.detections);
  }

  onStreamStatus(data: any) {
    // Handle stream status
    console.log('Stream status:', data.status);
  }

  onError(data: any) {
    // Handle errors
    console.error('Stream error:', data.message);
  }
}
```

### Python

```python
import asyncio
import websockets
import json
import base64

class VideoStreamClient:
    def __init__(self, token: str, client_id: str = None):
        self.token = token
        self.client_id = client_id
        self.websocket = None
        self.stream_id = None

    async def connect(self):
        url = f"ws://localhost:8000/ws/video-stream?token={self.token}&client_id={self.client_id}"
        self.websocket = await websockets.connect(url)
        await self.listen()

    async def start_stream(self, config: dict):
        self.stream_id = f"stream_{int(time.time())}"
        message = {
            "type": "start_stream",
            "data": {
                "stream_id": self.stream_id,
                "config": config
            }
        }
        await self.websocket.send(json.dumps(message))

    async def send_frame(self, frame_data: bytes, frame_number: int):
        frame_b64 = base64.b64encode(frame_data).decode('utf-8')
        message = {
            "type": "video_frame",
            "data": {
                "stream_id": self.stream_id,
                "frame_data": frame_b64,
                "frame_number": frame_number,
                "timestamp": datetime.now().isoformat()
            }
        }
        await self.websocket.send(json.dumps(message))

    async def listen(self):
        async for message in self.websocket:
            data = json.loads(message)
            await self.handle_message(data)

    async def handle_message(self, message: dict):
        message_type = message.get("type")
        data = message.get("data", {})

        if message_type == "detection_results":
            await self.on_detection_results(data)
        elif message_type == "stream_status":
            await self.on_stream_status(data)
        elif message_type == "error":
            await self.on_error(data)

    async def on_detection_results(self, data: dict):
        print(f"Detections: {data['detections']}")

    async def on_stream_status(self, data: dict):
        print(f"Stream status: {data['status']}")

    async def on_error(self, data: dict):
        print(f"Error: {data['message']}")
```

## Performance Considerations

### Frame Processing
- **Frame Size**: Smaller frames process faster
- **Frame Rate**: Limit to 30 FPS for optimal performance
- **Batch Processing**: Process multiple frames in batches

### Network Optimization
- **Compression**: Use WebSocket compression
- **Binary Data**: Consider binary frames for large data
- **Connection Pooling**: Reuse WebSocket connections

### Memory Management
- **Frame Buffering**: Limit buffer size to prevent memory leaks
- **Garbage Collection**: Regular cleanup of processed frames
- **Resource Monitoring**: Monitor memory usage

## Security Considerations

### Authentication
- **JWT Tokens**: Always authenticate WebSocket connections
- **Token Expiry**: Handle token expiration gracefully
- **Rate Limiting**: Implement rate limiting per connection

### Data Validation
- **Input Validation**: Validate all incoming data
- **Frame Validation**: Check frame format and size
- **Error Handling**: Secure error messages

## Monitoring and Debugging

### Connection Monitoring
```bash
# Check WebSocket connections
docker-compose logs backend | grep "WebSocket"

# Monitor connection count
curl http://localhost:8000/api/v1/utils/websocket-stats/
```

### Performance Metrics
- **FPS**: Frames per second processing
- **Latency**: End-to-end processing time
- **Memory Usage**: RAM consumption
- **CPU Usage**: Processing load

## Troubleshooting

### Common Issues

1. **Connection Drops**
   - Check network stability
   - Verify authentication token
   - Monitor server resources

2. **High Latency**
   - Reduce frame size
   - Lower frame rate
   - Check network conditions

3. **Memory Issues**
   - Reduce buffer size
   - Implement frame cleanup
   - Monitor memory usage

### Debug Mode

Enable debug logging:

```bash
# Set environment variable
LOG_LEVEL=DEBUG

# Restart backend
docker-compose restart backend
```

## Next Steps

- **[Person Detection API](person-detection.md)** - REST API for detection
- **[Analytics API](analytics.md)** - Analytics and reporting
- **[Authentication](authentication.md)** - JWT authentication setup

