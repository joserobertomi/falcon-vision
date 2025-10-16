# Person Detection Integration - WebSocket Video Streaming

## Overview

The WebSocket video streaming service has been successfully integrated with YOLOv8 person detection. Frames received from the `camera.py` frontend are now automatically processed with AI-powered person detection, and annotated frames (with bounding boxes) are sent back to clients in real-time.

## Architecture

```
┌─────────────┐         ┌──────────────────┐         ┌─────────────────┐
│  camera.py  │ ──────> │  streaming.py    │ ──────> │ frame_processor │
│  (Frontend) │  frames │  (WebSocket API) │  bytes  │   (YOLOv8 AI)   │
└─────────────┘         └──────────────────┘         └─────────────────┘
                                 │                            │
                                 │  <──────────────────────  │
                                 │     annotated frames       │
                                 v                            v
                        ┌─────────────────┐        ┌──────────────┐
                        │ connection_mgr  │        │ person_tracker│
                        │  (WebSocket)    │        │   (Original)  │
                        └─────────────────┘        └──────────────┘
```

## Components

### 1. `frame_processor.py` (NEW)
**Location**: `backend/app/cv_model/frame_processor.py`

A lightweight frame processing service specifically designed for WebSocket streaming:
- **Real-time Processing**: Processes individual frames without camera initialization
- **Person Detection**: Uses YOLOv8 nano model for fast person detection
- **Annotation**: Draws bounding boxes, confidence scores, and statistics
- **Optional QR Detection**: Can detect QR codes if enabled
- **Async Support**: Full async/await support for non-blocking processing

Key methods:
- `process_frame(frame_bytes)`: Main method that processes a single frame
- `detect_persons(frame)`: YOLOv8 person detection
- `detect_qr_codes(frame)`: Optional QR code detection
- `draw_info_overlay(frame, ...)`: Adds statistics overlay

### 2. `streaming.py` (UPDATED)
**Location**: `backend/app/api/routes/streaming.py`

Enhanced WebSocket endpoint with person detection:
- **Automatic Processing**: All incoming frames are processed with person detection
- **Configurable**: Per-client configuration for confidence threshold and QR detection
- **Real-time Results**: Sends both processed frames and detection metadata

## Features

### ✅ Real-time Person Detection
- Detects persons in video frames using YOLOv8
- Draws bounding boxes around detected persons
- Shows confidence scores for each detection
- Displays person count and average confidence

### ✅ Configurable Detection
- Adjustable confidence threshold (0.0 - 1.0)
- Optional QR code detection
- Per-client configuration via WebSocket messages

### ✅ Detection Metadata
- Person count
- Bounding box coordinates
- Confidence scores
- Frame processing statistics

### ✅ Visual Annotations
- Green bounding boxes around detected persons
- Confidence labels on each detection
- Statistics overlay showing:
  - Number of persons detected
  - QR codes detected (if enabled)
  - Average confidence
  - Total frames processed

## Usage

### 1. WebSocket Connection

Connect to the WebSocket endpoint with JWT authentication:

```javascript
const token = 'your-jwt-token';
const ws = new WebSocket(`ws://localhost:8000/api/v1/ws/video?token=${token}`);
```

### 2. Send Video Frames

Send frames as binary (Blob/ArrayBuffer):

```javascript
// Capture frame from video element
const canvas = document.createElement('canvas');
canvas.width = video.videoWidth;
canvas.height = video.videoHeight;
const ctx = canvas.getContext('2d');
ctx.drawImage(video, 0, 0);

canvas.toBlob((blob) => {
    ws.send(blob); // Send to server
}, 'image/jpeg', 0.8);
```

### 3. Receive Processed Frames

Receive annotated frames with person detection:

```javascript
ws.onmessage = (event) => {
    if (event.data instanceof Blob) {
        // Processed frame with bounding boxes
        const url = URL.createObjectURL(event.data);
        imgElement.src = url;
    } else {
        // Detection metadata (JSON)
        const data = JSON.parse(event.data);
        if (data.type === 'detection') {
            console.log(`Detected ${data.person_count} persons`);
            console.log(`Average confidence: ${data.avg_confidence}`);
            console.log('Detections:', data.detections);
        }
    }
};
```

### 4. Configure Detection (Optional)

Adjust detection settings on-the-fly:

```javascript
// Set confidence threshold to 0.6 (60%)
ws.send(JSON.stringify({
    action: 'configure',
    confidence: 0.6,
    enable_qr: false
}));

// Server responds with confirmation
// {"type": "config_updated", "confidence_threshold": 0.6, "enable_qr": false}
```

## WebSocket Protocol

### Client → Server Messages

#### Binary Messages (Video Frames)
```
Send: Raw frame data (JPEG, PNG, etc.)
Action: Frame is processed with person detection
```

#### Text Messages (JSON Control)
```json
// Ping/Heartbeat
{"action": "ping"}

// Request status
{"action": "status"}

// Configure detection
{
    "action": "configure",
    "confidence": 0.5,    // 0.0 - 1.0
    "enable_qr": false     // true/false
}
```

### Server → Client Messages

#### Binary Messages (Processed Frames)
```
Receive: Annotated frame with bounding boxes (JPEG)
```

#### JSON Messages

**Connection Confirmation:**
```json
{
    "type": "connection",
    "status": "connected",
    "client_id": "user-id",
    "user_email": "user@example.com",
    "message": "WebSocket connection established..."
}
```

**Detection Results (when persons detected):**
```json
{
    "type": "detection",
    "person_count": 2,
    "avg_confidence": 0.87,
    "detections": [
        {
            "bbox": [100, 150, 300, 450],
            "confidence": 0.89
        },
        {
            "bbox": [400, 200, 550, 480],
            "confidence": 0.85
        }
    ]
}
```

**Configuration Update:**
```json
{
    "type": "config_updated",
    "confidence_threshold": 0.6,
    "enable_qr": false
}
```

**Status Response:**
```json
{
    "type": "status",
    "client_id": "user-id",
    "active_connections": 3
}
```

**Heartbeat:**
```json
{"type": "heartbeat"}
```

## Configuration Options

### Default Settings
```python
detection_config = {
    "confidence_threshold": 0.5,  # Minimum confidence for detection (50%)
    "enable_qr": False             # QR code detection disabled
}
```

### Adjustable Parameters

**Confidence Threshold** (`confidence_threshold`)
- Range: 0.0 - 1.0
- Default: 0.5
- Lower values: More detections, potentially more false positives
- Higher values: Fewer detections, more confident results

**QR Code Detection** (`enable_qr`)
- Default: False
- When enabled: Also detects and highlights QR codes in frames

## Testing

### Using the Streamlit Frontend (`camera.py`)

1. **Start Backend:**
   ```bash
   cd backend
   python -m uvicorn app.api.main:app --reload
   ```

2. **Start Frontend:**
   ```bash
   cd ui
   streamlit run app/pages/camera.py
   ```

3. **Test Flow:**
   - Get JWT token from `/api/v1/login/access-token`
   - Enter token in the frontend
   - Click "Connect" to establish WebSocket connection
   - Click "Start Camera" to access webcam
   - Click "Start Streaming" to send frames
   - **Watch for green bounding boxes around detected persons!**

### Expected Behavior

✅ **When persons are in frame:**
- Green bounding boxes drawn around each person
- Confidence scores displayed (e.g., "Person 0.87")
- Statistics overlay showing person count
- Detection metadata sent as JSON

✅ **When no persons in frame:**
- Original frame returned with statistics overlay
- No bounding boxes
- Person count shows 0

✅ **Real-time updates:**
- Frames processed in real-time
- Minimal latency (depends on hardware)
- Continuous streaming

## Performance Considerations

### Model Selection
- **YOLOv8n (nano)**: Currently used - fastest, good for real-time
- **YOLOv8s (small)**: More accurate, slightly slower
- **YOLOv8m (medium)**: Best accuracy, requires more resources

To change model, edit `frame_processor.py`:
```python
self.model = YOLO('yolov8s.pt')  # Change from 'yolov8n.pt'
```

### Optimization Tips

1. **Frame Rate**: Adjust streaming FPS in frontend (default: 10 FPS)
2. **Frame Size**: Smaller frames = faster processing
3. **JPEG Quality**: Lower quality = smaller payload (currently 80%)
4. **Confidence Threshold**: Higher threshold = faster processing

### Hardware Requirements

- **CPU**: Multi-core processor recommended
- **RAM**: 4GB+ for model inference
- **GPU**: Optional, but highly recommended for better performance
- **Camera**: Any webcam compatible with browser WebRTC

## Troubleshooting

### Issue: No bounding boxes appearing
**Solutions:**
- Check if persons are clearly visible in frame
- Lower confidence threshold: `{"action": "configure", "confidence": 0.3}`
- Ensure good lighting conditions
- Check server logs for processing errors

### Issue: Slow processing/lag
**Solutions:**
- Reduce streaming FPS in frontend
- Use smaller frame resolution
- Check CPU/GPU usage
- Consider using YOLOv8n (nano) if not already

### Issue: Connection drops frequently
**Solutions:**
- Check network stability
- Verify JWT token hasn't expired
- Monitor server logs for errors
- Increase heartbeat timeout if needed

### Issue: Model not loading
**Solutions:**
- Install required dependencies:
  ```bash
  pip install ultralytics opencv-python numpy pyzbar
  ```
- Ensure YOLOv8 model downloads successfully (first run)
- Check disk space for model files

## Dependencies

Add to `requirements.txt`:
```txt
ultralytics>=8.0.0      # YOLOv8
opencv-python>=4.8.0    # Image processing
numpy>=1.24.0           # Array operations
pyzbar>=0.1.9           # QR code detection (optional)
```

Install:
```bash
pip install ultralytics opencv-python numpy pyzbar
```

## Future Enhancements

Potential improvements:
- [ ] Multi-object detection (not just persons)
- [ ] Object tracking across frames
- [ ] Face detection/recognition
- [ ] Activity recognition
- [ ] Recording with detections
- [ ] Detection alerts/notifications
- [ ] Analytics dashboard
- [ ] GPU acceleration toggle

## Summary

✅ **Integrated**: Person detection is now fully integrated into WebSocket streaming
✅ **Real-time**: Frames are processed and annotated in real-time
✅ **Configurable**: Detection settings can be adjusted per client
✅ **Automatic**: No changes needed to frontend code - just works!
✅ **Informative**: Provides both visual annotations and detection metadata

The system now automatically detects persons in video frames received from `camera.py` and returns annotated frames with bounding boxes, making it easy to see who is in the camera's view in real-time! 🎥✨

