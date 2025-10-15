# WebSocket Video Streaming Documentation

## Overview

This project includes a WebSocket endpoint for real-time video streaming. The implementation allows bidirectional video frame transmission between clients and the server, enabling use cases such as:

- Live camera feeds
- Real-time video processing
- Object detection and AI inference on video streams
- Broadcasting video to multiple clients
- Video conferencing capabilities

## Endpoint

**WebSocket URL:** `ws://<host>:<port>/api/v1/ws/video/{client_id}`

- **Protocol:** WebSocket
- **Path Parameters:**
  - `client_id` (string, required): A unique identifier for the client connection

### Example URLs

- Local development: `ws://localhost:8000/api/v1/ws/video/client123`
- Production: `wss://yourdomain.com/api/v1/ws/video/client123`

## Features

### 1. Connection Management
- Automatic connection handling with heartbeat mechanism
- Multiple concurrent client connections
- Connection status tracking
- Automatic cleanup of disconnected clients

### 2. Video Frame Transmission
- **Binary Messages**: Video frames (JPEG, PNG, or raw frame data)
- **Bidirectional**: Clients can send and receive frames
- **Echo Mode**: Server echoes frames back to sender (useful for testing)
- **Broadcast Mode**: Distribute frames to all connected clients

### 3. Control Messages
Text messages in JSON format for control operations:

```json
// Ping (heartbeat)
{"action": "ping"}

// Request connection status
{"action": "status"}

// Broadcast a frame to all clients
{
  "action": "broadcast",
  "data": "<base64_encoded_frame>"
}
```

## Protocol Messages

### Server → Client Messages

#### Connection Confirmation
```json
{
  "type": "connection",
  "status": "connected",
  "client_id": "client123",
  "message": "WebSocket connection established for video streaming"
}
```

#### Heartbeat
```json
{
  "type": "heartbeat"
}
```

#### Pong Response
```json
{
  "type": "pong",
  "timestamp": 1634567890.123
}
```

#### Status Response
```json
{
  "type": "status",
  "client_id": "client123",
  "active_connections": 5
}
```

#### Broadcast Result
```json
{
  "type": "broadcast_result",
  "sent_to": 4
}
```

#### Error Message
```json
{
  "type": "error",
  "message": "Error description"
}
```

### Client → Server Messages

#### Text Control Messages
```json
// Ping
{"action": "ping"}

// Request status
{"action": "status"}

// Broadcast frame
{"action": "broadcast", "data": "base64_encoded_frame"}
```

#### Binary Messages
Send raw video frame data as binary (Blob, ArrayBuffer, etc.)

## Usage Examples

### JavaScript/TypeScript Client

```javascript
// Connect to WebSocket
const clientId = 'client_' + Date.now();
const ws = new WebSocket(`ws://localhost:8000/api/v1/ws/video/${clientId}`);

// Connection event handlers
ws.onopen = () => {
    console.log('Connected to video streaming server');
};

ws.onmessage = (event) => {
    if (event.data instanceof Blob) {
        // Handle received video frame
        displayVideoFrame(event.data);
    } else {
        // Handle control message
        const data = JSON.parse(event.data);
        console.log('Received:', data);
    }
};

ws.onerror = (error) => {
    console.error('WebSocket error:', error);
};

ws.onclose = () => {
    console.log('Disconnected from server');
};

// Send video frame from canvas
function sendVideoFrame(canvas) {
    canvas.toBlob((blob) => {
        if (ws.readyState === WebSocket.OPEN) {
            ws.send(blob);
        }
    }, 'image/jpeg', 0.8);
}

// Send control message
function sendPing() {
    ws.send(JSON.stringify({ action: 'ping' }));
}

// Display received frame
function displayVideoFrame(blob) {
    const url = URL.createObjectURL(blob);
    const img = document.getElementById('video-frame');
    img.onload = () => URL.revokeObjectURL(url);
    img.src = url;
}
```

### Python Client

```python
import asyncio
import websockets
import cv2
import json

async def video_streaming_client():
    uri = "ws://localhost:8000/api/v1/ws/video/python_client"
    
    async with websockets.connect(uri) as websocket:
        # Receive connection confirmation
        message = await websocket.recv()
        print(f"Connected: {message}")
        
        # Open camera
        cap = cv2.VideoCapture(0)
        
        try:
            while True:
                # Capture frame
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Encode frame as JPEG
                _, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                
                # Send frame
                await websocket.send(frame_bytes)
                
                # Receive processed frame or response
                response = await websocket.recv()
                
                if isinstance(response, bytes):
                    # Received a video frame
                    print(f"Received frame: {len(response)} bytes")
                else:
                    # Received control message
                    data = json.loads(response)
                    print(f"Received: {data}")
                
                await asyncio.sleep(0.1)  # 10 FPS
                
        finally:
            cap.release()

# Run the client
asyncio.run(video_streaming_client())
```

### React Component Example

```tsx
import React, { useEffect, useRef, useState } from 'react';

const VideoStreaming: React.FC = () => {
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const receivedImageRef = useRef<HTMLImageElement>(null);
  
  useEffect(() => {
    // Connect to WebSocket
    const clientId = `client_${Date.now()}`;
    const ws = new WebSocket(
      `ws://localhost:8000/api/v1/ws/video/${clientId}`
    );
    
    ws.onopen = () => {
      setConnected(true);
      console.log('Connected');
    };
    
    ws.onmessage = (event) => {
      if (event.data instanceof Blob) {
        // Display received frame
        const url = URL.createObjectURL(event.data);
        if (receivedImageRef.current) {
          receivedImageRef.current.src = url;
        }
      } else {
        const data = JSON.parse(event.data);
        console.log('Received:', data);
      }
    };
    
    ws.onclose = () => {
      setConnected(false);
      console.log('Disconnected');
    };
    
    wsRef.current = ws;
    
    return () => {
      ws.close();
    };
  }, []);
  
  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480 }
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (error) {
      console.error('Camera error:', error);
    }
  };
  
  const captureAndSend = () => {
    if (!videoRef.current || !canvasRef.current) return;
    
    const canvas = canvasRef.current;
    const video = videoRef.current;
    const ctx = canvas.getContext('2d');
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx?.drawImage(video, 0, 0);
    
    canvas.toBlob((blob) => {
      if (blob && wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(blob);
      }
    }, 'image/jpeg', 0.8);
  };
  
  return (
    <div>
      <h2>Video Streaming</h2>
      <p>Status: {connected ? 'Connected' : 'Disconnected'}</p>
      
      <div>
        <video ref={videoRef} autoPlay muted />
        <canvas ref={canvasRef} style={{ display: 'none' }} />
      </div>
      
      <div>
        <h3>Received Frame</h3>
        <img ref={receivedImageRef} alt="Received frame" />
      </div>
      
      <button onClick={startCamera}>Start Camera</button>
      <button onClick={captureAndSend}>Capture & Send</button>
    </div>
  );
};

export default VideoStreaming;
```

## Testing

### Using the Test Client

A complete HTML test client is provided at:
`backend/app/api/routes/websocket_test_client.html`

To use it:

1. Ensure your FastAPI server is running
2. Open the HTML file in a web browser
3. Click "Connect" to establish the WebSocket connection
4. Click "Start Camera" to access your webcam
5. Click "Start Streaming" to send video frames

### REST API Endpoint

Check the number of active connections:

```bash
curl http://localhost:8000/api/v1/ws/video/connections/count
```

Response:
```json
{
  "active_connections": 3
}
```

## Configuration

### CORS Settings

Ensure your CORS settings in the FastAPI app allow WebSocket connections from your frontend domain. Update `backend/app/main.py` if needed:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Timeout Settings

The WebSocket connection has a 30-second timeout for heartbeat checks. This can be adjusted in `video_streaming.py`:

```python
data = await asyncio.wait_for(
    websocket.receive(),
    timeout=30.0  # Adjust this value
)
```

## Integration Examples

### Adding Video Processing

Modify the WebSocket endpoint to process frames:

```python
@router.websocket("/ws/video/{client_id}")
async def video_stream_endpoint(websocket: WebSocket, client_id: str) -> None:
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            data = await websocket.receive()
            
            if "bytes" in data:
                frame_data = data["bytes"]
                
                # Process frame (example: object detection)
                processed_frame = await process_video_frame(frame_data)
                
                # Send processed frame back
                await websocket.send_bytes(processed_frame)
    
    except WebSocketDisconnect:
        manager.disconnect(client_id)

async def process_video_frame(frame_bytes: bytes) -> bytes:
    # Your processing logic here
    # Example: run ML model, object detection, etc.
    return frame_bytes
```

### Broadcasting to Multiple Clients

```python
# In your endpoint, broadcast received frames to all clients
if "bytes" in data:
    frame_data = data["bytes"]
    
    # Broadcast to all other clients
    for other_client_id in manager.active_connections:
        if other_client_id != client_id:
            await manager.send_frame(other_client_id, frame_data)
```

## Performance Considerations

### Frame Rate
- **Recommended**: 10-30 FPS for most applications
- **High-performance**: 30-60 FPS (requires more bandwidth and processing)
- **Low-bandwidth**: 5-10 FPS

### Frame Quality
- JPEG quality: 0.7-0.9 for good balance
- Lower quality (0.5-0.7) for bandwidth-constrained environments
- PNG for lossless quality (larger file size)

### Resolution
- **Standard**: 640x480
- **HD**: 1280x720
- **Full HD**: 1920x1080 (requires significant bandwidth)

### Bandwidth Calculation

Approximate bandwidth per client:
```
Bandwidth (Mbps) = (Frame Size KB × FPS × 8) / 1024

Example: 
- Frame size: 50 KB
- FPS: 20
- Bandwidth: (50 × 20 × 8) / 1024 ≈ 7.8 Mbps
```

## Troubleshooting

### Connection Issues

**Problem**: WebSocket fails to connect

**Solutions**:
- Check if the server is running
- Verify the WebSocket URL is correct
- Check CORS settings
- Ensure firewall allows WebSocket connections
- For production, use `wss://` (secure WebSocket)

### Frame Not Displaying

**Problem**: Frames are sent but not displayed

**Solutions**:
- Check browser console for errors
- Verify frame format (JPEG, PNG)
- Check if Blob URL is being created and revoked properly
- Inspect network tab to confirm frames are being received

### Performance Issues

**Problem**: Lag or dropped frames

**Solutions**:
- Reduce frame rate
- Decrease frame quality
- Lower resolution
- Check network bandwidth
- Monitor server CPU/memory usage

## Security Considerations

### Authentication

Add authentication to the WebSocket endpoint:

```python
from app.api.deps import get_current_user

@router.websocket("/ws/video/{client_id}")
async def video_stream_endpoint(
    websocket: WebSocket, 
    client_id: str,
    token: str = Query(...)
) -> None:
    # Verify token
    try:
        user = await verify_websocket_token(token)
    except Exception:
        await websocket.close(code=1008, reason="Unauthorized")
        return
    
    await manager.connect(websocket, client_id)
    # ... rest of implementation
```

### Rate Limiting

Implement rate limiting to prevent abuse:

```python
from collections import defaultdict
from time import time

rate_limits = defaultdict(list)

async def check_rate_limit(client_id: str, max_frames_per_second: int = 30) -> bool:
    now = time()
    rate_limits[client_id] = [
        t for t in rate_limits[client_id] if now - t < 1.0
    ]
    
    if len(rate_limits[client_id]) >= max_frames_per_second:
        return False
    
    rate_limits[client_id].append(now)
    return True
```

### Data Validation

Validate frame size and format:

```python
MAX_FRAME_SIZE = 5 * 1024 * 1024  # 5 MB

if "bytes" in data:
    frame_data = data["bytes"]
    
    if len(frame_data) > MAX_FRAME_SIZE:
        await websocket.send_json({
            "type": "error",
            "message": "Frame size exceeds limit"
        })
        continue
```

## Deployment

### Production Checklist

- [ ] Use `wss://` (secure WebSocket over TLS)
- [ ] Configure proper CORS settings
- [ ] Implement authentication and authorization
- [ ] Add rate limiting
- [ ] Set up monitoring and logging
- [ ] Configure load balancing if needed
- [ ] Test with multiple concurrent connections
- [ ] Set appropriate connection timeouts
- [ ] Implement reconnection logic on client side

### Nginx Configuration

Example Nginx configuration for WebSocket proxy:

```nginx
location /api/v1/ws/ {
    proxy_pass http://backend:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_read_timeout 86400;
}
```

## API Reference

### ConnectionManager Class

#### Methods

- `connect(websocket: WebSocket, client_id: str) -> None`
  - Accepts a new WebSocket connection

- `disconnect(client_id: str) -> None`
  - Removes a WebSocket connection

- `send_frame(client_id: str, frame: bytes) -> bool`
  - Sends a frame to a specific client

- `broadcast_frame(frame: bytes) -> int`
  - Broadcasts a frame to all connected clients
  - Returns the number of successful sends

- `send_text(client_id: str, message: str) -> bool`
  - Sends a text message to a specific client

- `get_active_connections_count() -> int`
  - Returns the number of active connections

## License

This implementation is part of the falcon-vision project and follows the same license terms.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the examples
3. Check server logs for error messages
4. Open an issue in the project repository

