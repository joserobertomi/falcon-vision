# WebSocket Video Streaming - Quick Start Guide

## What's Been Added

A complete WebSocket endpoint for real-time video streaming has been added to the Falcon Vision project.

## Files Added/Modified

### New Files
1. **`backend/app/api/routes/video_streaming.py`** - Main WebSocket endpoint implementation
2. **`backend/app/api/routes/websocket_client_example.py`** - Python client example
3. **`docs/websocket_video_streaming.md`** - Complete documentation
4. **`docs/websocket_quickstart.md`** - This file

### Modified Files
1. **`backend/app/api/main.py`** - Added video_streaming router to API

## Quick Start

### 1. Start the Server

Make sure your FastAPI server is running:

```bash
cd backend
docker-compose up
# or
uvicorn app.main:app --reload
```

The WebSocket endpoint will be available at:
- **Local:** `ws://localhost:8000/api/v1/ws/video/{client_id}`

### 3. Test with Python Client

```bash
# Install dependencies
pip install websockets opencv-python

# Run the client
cd backend/app/api/routes
python websocket_client_example.py
```

Follow the interactive menu to:
- Stream from your camera
- Stream from a video file
- Send test patterns
- Send control messages

### 4. Use in Your JavaScript Application

```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/video/my_client');

ws.onopen = () => console.log('Connected');

ws.onmessage = (event) => {
    if (event.data instanceof Blob) {
        // Display video frame
        const img = document.getElementById('video-frame');
        img.src = URL.createObjectURL(event.data);
    }
};

// Send video frame
function sendFrame(canvas) {
    canvas.toBlob((blob) => {
        ws.send(blob);
    }, 'image/jpeg', 0.8);
}
```

## API Endpoints

### WebSocket Endpoint
```
ws://localhost:8000/api/v1/ws/video/{client_id}
```

### REST Endpoint (Check Connections)
```
GET http://localhost:8000/api/v1/ws/video/connections/count
```

## Features

✅ **Bidirectional video streaming**
✅ **Multiple concurrent connections**
✅ **Automatic heartbeat/keepalive**
✅ **Connection management**
✅ **Broadcast capability**
✅ **Control messages (ping, status)**
✅ **Frame echo for testing**

## Protocol

### Send Video Frame
- Send binary data (JPEG/PNG encoded image)

### Send Control Message
- Send JSON text messages:
  ```json
  {"action": "ping"}
  {"action": "status"}
  {"action": "broadcast", "data": "base64_frame"}
  ```

### Receive Messages
- **Binary**: Video frames
- **JSON**: Control responses and status updates

## Common Use Cases

### 1. Live Camera Feed
Stream from webcam to server for processing (object detection, AI inference, etc.)

### 2. Video Broadcasting
One client sends video, server broadcasts to all connected clients

### 3. Video Processing Pipeline
Client → Server (process/analyze) → Client (receive processed result)

### 4. Multi-Camera Setup
Multiple cameras streaming simultaneously to a central server

## Next Steps

1. **Read Full Documentation**: See `docs/websocket_video_streaming.md`
2. **Add Authentication**: Implement token-based auth for production
3. **Add Video Processing**: Integrate AI/ML models for frame analysis
4. **Scale**: Add load balancing for multiple servers
5. **Monitor**: Add logging and metrics

## Troubleshooting

### "Connection refused"
- Ensure the server is running
- Check the port number (default: 8000)

### "Camera not accessible"
- Grant camera permissions in browser
- Check if another app is using the camera

### "Frames not appearing"
- Check browser console for errors
- Verify the frame format (JPEG/PNG)
- Check network tab to confirm data is being sent/received

### High latency
- Reduce FPS
- Lower image quality
- Decrease resolution

## Examples Directory

- **HTML Client**: `backend/app/api/routes/websocket_test_client.html`
- **Python Client**: `backend/app/api/routes/websocket_client_example.py`
- **Full Docs**: `docs/websocket_video_streaming.md`

## Support

For detailed information, see the complete documentation at:
`docs/websocket_video_streaming.md`

---

**Ready to stream! 🎥**

