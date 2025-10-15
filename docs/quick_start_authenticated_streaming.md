# Quick Start: Authenticated WebSocket Video Streaming

## Prerequisites

- Backend server running on `http://localhost:8000`
- Valid user account in the database
- Streamlit frontend running (optional, for UI testing)

## Step 1: Start the Backend

```bash
cd backend
uvicorn app.main:app --reload
```

Server should be running at `http://localhost:8000`

## Step 2: Get Your JWT Token

### Option A: Using curl

```bash
curl -X POST "http://localhost:8000/api/v1/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=your-email@example.com&password=your-password"
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MDk2NTY...",
  "token_type": "bearer"
}
```

### Option B: Using API Docs

1. Go to `http://localhost:8000/docs`
2. Click the "Authorize" button (🔓)
3. Enter your username and password
4. Click "Authorize" again
5. Navigate to `/login/access-token` endpoint
6. Execute the request to get your token

### Option C: Using Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/login/access-token",
    data={
        "username": "your-email@example.com",
        "password": "your-password"
    }
)

token = response.json()["access_token"]
print(f"Your token: {token}")
```

## Step 3: Connect to WebSocket

### Option A: Using Streamlit Interface (Recommended)

1. Start Streamlit:
   ```bash
   cd beta-frontend
   streamlit run app/main.py
   ```

2. Navigate to the "Camera" page in the sidebar

3. Paste your JWT token in the "JWT Access Token" field

4. Click "Connect"

5. Click "Start Camera" to access your webcam

6. Click "Start Streaming" to begin sending video frames

### Option B: Using JavaScript

```javascript
// Your JWT token from Step 2
const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...';

// Connect to WebSocket with token
const ws = new WebSocket(`ws://localhost:8000/api/v1/ws/video?token=${encodeURIComponent(token)}`);

ws.onopen = () => {
    console.log('✅ Connected successfully!');
};

ws.onmessage = (event) => {
    if (event.data instanceof Blob) {
        // Received video frame
        console.log('Received frame:', event.data.size, 'bytes');
        
        // Display frame in an image element
        const img = document.getElementById('video-frame');
        img.src = URL.createObjectURL(event.data);
    } else {
        // Received JSON message
        const data = JSON.parse(event.data);
        console.log('Received message:', data);
    }
};

ws.onerror = (error) => {
    console.error('❌ WebSocket error:', error);
};

ws.onclose = (event) => {
    if (event.code === 1008) {
        console.error('❌ Authentication failed. Token invalid or expired.');
    } else {
        console.log('Connection closed:', event.code, event.reason);
    }
};

// Send a test message
ws.send(JSON.stringify({ action: 'ping' }));
```

### Option C: Using Python Client

```python
import asyncio
import websockets
import json

async def test_streaming():
    # Your JWT token
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    
    # Connect with authentication
    uri = f"ws://localhost:8000/api/v1/ws/video?token={token}"
    
    async with websockets.connect(uri) as websocket:
        # Receive connection confirmation
        response = await websocket.recv()
        print(f"Connected: {response}")
        
        # Send ping
        await websocket.send(json.dumps({"action": "ping"}))
        pong = await websocket.recv()
        print(f"Pong: {pong}")
        
        # Request status
        await websocket.send(json.dumps({"action": "status"}))
        status = await websocket.recv()
        print(f"Status: {status}")

# Run the test
asyncio.run(test_streaming())
```

## Step 4: Send Video Frames

### Using JavaScript with Webcam

```javascript
// Get camera stream
const stream = await navigator.mediaDevices.getUserMedia({
    video: { width: 640, height: 480 }
});

// Display in video element
const video = document.getElementById('localVideo');
video.srcObject = stream;

// Capture and send frames
async function captureAndSend() {
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);
    
    canvas.toBlob((blob) => {
        if (ws.readyState === WebSocket.OPEN) {
            ws.send(blob);
            console.log('Frame sent:', blob.size, 'bytes');
        }
    }, 'image/jpeg', 0.8);
}

// Send frames at 10 FPS
const fps = 10;
setInterval(captureAndSend, 1000 / fps);
```

## Troubleshooting

### Error: "Authentication failed"

**Cause**: Invalid or expired token

**Solution**:
1. Get a fresh token from `/api/v1/login/access-token`
2. Make sure you're copying the entire token
3. Check that your user account is active

### Error: "Connection refused"

**Cause**: Backend server is not running

**Solution**:
```bash
cd backend
uvicorn app.main:app --reload
```

### Error: "Token validation failed"

**Cause**: Token is malformed or SECRET_KEY mismatch

**Solution**:
1. Verify the token format is correct
2. Ensure SECRET_KEY environment variable is set correctly
3. Try logging in again to get a new token

### Camera not accessible

**Cause**: Browser permissions not granted

**Solution**:
1. Click "Allow" when prompted for camera access
2. Check browser settings to ensure camera is enabled
3. Try using HTTPS instead of HTTP (required by some browsers)

### Frames not being received

**Cause**: Processing or network issues

**Solution**:
1. Check browser console for errors
2. Verify backend logs for processing errors
3. Try reducing FPS or frame quality
4. Check network connectivity

## Testing the Connection

### Test 1: Ping-Pong

```javascript
// Send ping
ws.send(JSON.stringify({ action: 'ping' }));

// Expect response: {"type": "pong", "timestamp": 1234567890.123}
```

### Test 2: Status Check

```javascript
// Request status
ws.send(JSON.stringify({ action: 'status' }));

// Expect response: {
//   "type": "status",
//   "client_id": "user-uuid",
//   "active_connections": 1
// }
```

### Test 3: Frame Echo

```javascript
// Send a test frame (e.g., from canvas or file)
const testBlob = new Blob(['test frame data'], { type: 'image/jpeg' });
ws.send(testBlob);

// Server should echo it back
ws.onmessage = (event) => {
    if (event.data instanceof Blob) {
        console.log('✅ Frame echoed back successfully!');
    }
};
```

## Next Steps

1. **Add frame processing**: Modify `streaming.py` to process frames (e.g., AI inference)
2. **Add broadcasting**: Uncomment broadcast functionality to share frames between clients
3. **Implement recording**: Save frames to disk or cloud storage
4. **Add analytics**: Track streaming metrics and user behavior
5. **Enhance UI**: Customize the Streamlit interface for your use case

## Security Best Practices

1. **Use HTTPS/WSS in production**: Always use secure connections
2. **Rotate tokens**: Implement token refresh mechanism
3. **Rate limiting**: Add rate limits to prevent abuse
4. **Frame validation**: Validate frame size and format
5. **Audit logging**: Log all connection and streaming events

## API Reference

### WebSocket Endpoint

- **URL**: `/ws/video`
- **Protocol**: WebSocket (ws:// or wss://)
- **Authentication**: JWT token as query parameter
- **Binary Messages**: Video frames (JPEG/PNG)
- **Text Messages**: JSON control messages

### Control Messages

| Action | Request | Response |
|--------|---------|----------|
| Ping | `{"action": "ping"}` | `{"type": "pong", "timestamp": ...}` |
| Status | `{"action": "status"}` | `{"type": "status", "client_id": "...", "active_connections": N}` |
| Broadcast | `{"action": "broadcast", "data": "base64..."}` | `{"type": "broadcast_result", "sent_to": N}` |

### Connection Events

| Event | Response |
|-------|----------|
| Connect | `{"type": "connection", "status": "connected", "client_id": "...", "user_email": "..."}` |
| Heartbeat | `{"type": "heartbeat"}` (every 30 seconds) |
| Error | `{"type": "error", "message": "..."}` |

## Support

- **Documentation**: Check `/docs/authentication_updates.md` for detailed info
- **API Docs**: Visit `http://localhost:8000/docs`
- **Logs**: Check backend logs for detailed error messages
- **Issues**: File issues on your project repository

Happy streaming! 🎥✨

