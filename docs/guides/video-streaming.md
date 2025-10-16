# Video Streaming Guide

## Overview

This guide covers the video streaming implementation in Falcon Vision, including WebSocket setup, real-time processing, and client integration.

## WebSocket Architecture

### WebSocket Server Setup
```python
# WebSocket server configuration
from fastapi import WebSocket, WebSocketDisconnect
from typing import List
import asyncio
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove disconnected connections
                self.active_connections.remove(connection)

manager = ConnectionManager()
```

### WebSocket Endpoint
```python
# WebSocket endpoint for video streaming
@app.websocket("/ws/video-stream")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Receive video frame data
            data = await websocket.receive_bytes()
            
            # Process frame for person detection
            detections = await process_video_frame(data)
            
            # Send detection results back
            response = {
                "type": "detection",
                "detections": detections,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await manager.send_personal_message(
                json.dumps(response), 
                websocket
            )
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

## Video Processing Pipeline

### Frame Processing
```python
# Video frame processing
import cv2
import numpy as np
from ultralytics import YOLO

class VideoProcessor:
    def __init__(self):
        self.model = YOLO('yolov8n.pt')
        self.confidence_threshold = 0.5
    
    async def process_frame(self, frame_data: bytes) -> List[dict]:
        # Decode frame
        nparr = np.frombuffer(frame_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Run detection
        results = self.model(frame, conf=self.confidence_threshold)
        
        # Extract person detections
        detections = []
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    if int(box.cls[0]) == 0:  # Person class
                        detection = {
                            "bbox": {
                                "x1": int(box.xyxy[0][0]),
                                "y1": int(box.xyxy[0][1]),
                                "x2": int(box.xyxy[0][2]),
                                "y2": int(box.xyxy[0][3])
                            },
                            "confidence": float(box.conf[0]),
                            "class_id": 0,
                            "class_name": "person"
                        }
                        detections.append(detection)
        
        return detections

video_processor = VideoProcessor()
```

### Real-time Processing
```python
# Real-time video processing
async def process_video_stream(websocket: WebSocket):
    while True:
        try:
            # Receive frame data
            frame_data = await websocket.receive_bytes()
            
            # Process frame
            detections = await video_processor.process_frame(frame_data)
            
            # Send results
            response = {
                "type": "detection",
                "detections": detections,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await websocket.send_text(json.dumps(response))
            
        except WebSocketDisconnect:
            break
        except Exception as e:
            logger.error(f"Error processing video: {e}")
            break
```

## Client-Side Integration

### WebSocket Client
```typescript
// WebSocket client for video streaming
class VideoStreamClient {
  private ws: WebSocket | null = null;
  private onDetection: (detections: Detection[]) => void;
  private onError: (error: Error) => void;
  
  constructor(
    onDetection: (detections: Detection[]) => void,
    onError: (error: Error) => void
  ) {
    this.onDetection = onDetection;
    this.onError = onError;
  }
  
  connect(url: string): void {
    this.ws = new WebSocket(url);
    
    this.ws.onopen = () => {
      console.log('WebSocket connected');
    };
    
    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'detection') {
          this.onDetection(data.detections);
        }
      } catch (error) {
        this.onError(error as Error);
      }
    };
    
    this.ws.onerror = (error) => {
      this.onError(error as Error);
    };
    
    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
    };
  }
  
  sendFrame(frameData: ArrayBuffer): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(frameData);
    }
  }
  
  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}
```

### Video Capture
```typescript
// Video capture and streaming
class VideoCapture {
  private video: HTMLVideoElement;
  private canvas: HTMLCanvasElement;
  private ctx: CanvasRenderingContext2D;
  private streamClient: VideoStreamClient;
  private isStreaming: boolean = false;
  
  constructor(
    videoElement: HTMLVideoElement,
    onDetection: (detections: Detection[]) => void,
    onError: (error: Error) => void
  ) {
    this.video = videoElement;
    this.canvas = document.createElement('canvas');
    this.ctx = this.canvas.getContext('2d')!;
    this.streamClient = new VideoStreamClient(onDetection, onError);
  }
  
  async startCamera(): Promise<void> {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480 }
      });
      
      this.video.srcObject = stream;
      this.video.play();
      
      // Connect to WebSocket
      this.streamClient.connect('ws://localhost:8000/ws/video-stream');
      
      // Start frame capture
      this.startFrameCapture();
      
    } catch (error) {
      throw new Error('Failed to access camera');
    }
  }
  
  private startFrameCapture(): void {
    const captureFrame = () => {
      if (this.isStreaming && this.video.readyState === 4) {
        // Draw video frame to canvas
        this.canvas.width = this.video.videoWidth;
        this.canvas.height = this.video.videoHeight;
        this.ctx.drawImage(this.video, 0, 0);
        
        // Convert canvas to blob
        this.canvas.toBlob((blob) => {
          if (blob) {
            // Convert blob to ArrayBuffer
            blob.arrayBuffer().then((arrayBuffer) => {
              this.streamClient.sendFrame(arrayBuffer);
            });
          }
        }, 'image/jpeg', 0.8);
      }
      
      requestAnimationFrame(captureFrame);
    };
    
    this.isStreaming = true;
    captureFrame();
  }
  
  stopCamera(): void {
    this.isStreaming = false;
    this.streamClient.disconnect();
    
    if (this.video.srcObject) {
      const stream = this.video.srcObject as MediaStream;
      stream.getTracks().forEach(track => track.stop());
      this.video.srcObject = null;
    }
  }
}
```

## React Integration

### Video Streaming Component
```typescript
// Video streaming React component
import React, { useRef, useEffect, useState } from 'react';

interface Detection {
  bbox: {
    x1: number;
    y1: number;
    x2: number;
    y2: number;
  };
  confidence: number;
  class_id: number;
  class_name: string;
}

const VideoStream: React.FC = () => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [detections, setDetections] = useState<Detection[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    let videoCapture: VideoCapture | null = null;
    
    if (isStreaming && videoRef.current) {
      videoCapture = new VideoCapture(
        videoRef.current,
        (newDetections) => setDetections(newDetections),
        (err) => setError(err.message)
      );
      
      videoCapture.startCamera().catch((err) => {
        setError(err.message);
        setIsStreaming(false);
      });
    }
    
    return () => {
      if (videoCapture) {
        videoCapture.stopCamera();
      }
    };
  }, [isStreaming]);
  
  const toggleStreaming = () => {
    setIsStreaming(!isStreaming);
    setError(null);
  };
  
  return (
    <div className="video-stream">
      <div className="video-container">
        <video
          ref={videoRef}
          width={640}
          height={480}
          autoPlay
          muted
        />
        <canvas
          ref={canvasRef}
          width={640}
          height={480}
          style={{ position: 'absolute', top: 0, left: 0 }}
        />
      </div>
      
      <div className="controls">
        <button onClick={toggleStreaming}>
          {isStreaming ? 'Stop' : 'Start'} Streaming
        </button>
      </div>
      
      {error && (
        <div className="error">
          Error: {error}
        </div>
      )}
      
      <div className="detections">
        <h3>Detections ({detections.length})</h3>
        {detections.map((detection, index) => (
          <div key={index} className="detection">
            <p>Confidence: {(detection.confidence * 100).toFixed(1)}%</p>
            <p>Bounding Box: ({detection.bbox.x1}, {detection.bbox.y1}) - ({detection.bbox.x2}, {detection.bbox.y2})</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default VideoStream;
```

## Performance Optimization

### Frame Rate Control
```typescript
// Frame rate control
class FrameRateController {
  private targetFPS: number;
  private lastFrameTime: number = 0;
  private frameInterval: number;
  
  constructor(targetFPS: number = 10) {
    this.targetFPS = targetFPS;
    this.frameInterval = 1000 / targetFPS;
  }
  
  shouldCaptureFrame(): boolean {
    const now = Date.now();
    if (now - this.lastFrameTime >= this.frameInterval) {
      this.lastFrameTime = now;
      return true;
    }
    return false;
  }
}
```

### Image Compression
```typescript
// Image compression for WebSocket
class ImageCompressor {
  private quality: number;
  
  constructor(quality: number = 0.8) {
    this.quality = quality;
  }
  
  compressImage(canvas: HTMLCanvasElement): Promise<ArrayBuffer> {
    return new Promise((resolve) => {
      canvas.toBlob(
        (blob) => {
          if (blob) {
            blob.arrayBuffer().then(resolve);
          }
        },
        'image/jpeg',
        this.quality
      );
    });
  }
}
```

### Memory Management
```typescript
// Memory management for video processing
class MemoryManager {
  private maxFrames: number;
  private frameQueue: ArrayBuffer[] = [];
  
  constructor(maxFrames: number = 10) {
    this.maxFrames = maxFrames;
  }
  
  addFrame(frame: ArrayBuffer): void {
    this.frameQueue.push(frame);
    
    // Remove old frames to prevent memory leaks
    if (this.frameQueue.length > this.maxFrames) {
      this.frameQueue.shift();
    }
  }
  
  clearFrames(): void {
    this.frameQueue = [];
  }
}
```

## Error Handling

### WebSocket Error Handling
```typescript
// WebSocket error handling
class WebSocketErrorHandler {
  private maxRetries: number;
  private retryDelay: number;
  private retryCount: number = 0;
  
  constructor(maxRetries: number = 5, retryDelay: number = 1000) {
    this.maxRetries = maxRetries;
    this.retryDelay = retryDelay;
  }
  
  async handleError(error: Error, reconnectFn: () => void): Promise<void> {
    if (this.retryCount < this.maxRetries) {
      this.retryCount++;
      console.log(`Retrying connection (${this.retryCount}/${this.maxRetries})...`);
      
      await new Promise(resolve => setTimeout(resolve, this.retryDelay));
      reconnectFn();
    } else {
      console.error('Max retries reached. Connection failed.');
      throw error;
    }
  }
  
  resetRetryCount(): void {
    this.retryCount = 0;
  }
}
```

### Camera Error Handling
```typescript
// Camera error handling
class CameraErrorHandler {
  static async handleCameraError(error: Error): Promise<string> {
    if (error.name === 'NotAllowedError') {
      return 'Camera access denied. Please allow camera access and try again.';
    } else if (error.name === 'NotFoundError') {
      return 'No camera found. Please connect a camera and try again.';
    } else if (error.name === 'NotReadableError') {
      return 'Camera is already in use by another application.';
    } else {
      return 'Failed to access camera. Please try again.';
    }
  }
}
```

## Testing

### WebSocket Testing
```python
# WebSocket testing
import asyncio
import websockets
import json

async def test_websocket_connection():
    uri = "ws://localhost:8000/ws/video-stream"
    
    async with websockets.connect(uri) as websocket:
        # Send test frame
        test_frame = b"test_frame_data"
        await websocket.send(test_frame)
        
        # Receive response
        response = await websocket.recv()
        data = json.loads(response)
        
        assert data["type"] == "detection"
        assert "detections" in data
        assert "timestamp" in data

# Run test
asyncio.run(test_websocket_connection())
```

### Frontend Testing
```typescript
// Frontend video streaming tests
describe('VideoStream', () => {
  it('should start camera when start button is clicked', async () => {
    const { getByText } = render(<VideoStream />);
    const startButton = getByText('Start Streaming');
    
    fireEvent.click(startButton);
    
    await waitFor(() => {
      expect(getByText('Stop Streaming')).toBeInTheDocument();
    });
  });
  
  it('should display detections when received', async () => {
    const mockDetections = [
      {
        bbox: { x1: 100, y1: 100, x2: 200, y2: 200 },
        confidence: 0.95,
        class_id: 0,
        class_name: 'person'
      }
    ];
    
    const { getByText } = render(<VideoStream />);
    
    // Simulate receiving detections
    act(() => {
      // Trigger detection update
    });
    
    expect(getByText('Detections (1)')).toBeInTheDocument();
  });
});
```

## Security Considerations

### WebSocket Security
```python
# WebSocket security
from fastapi import WebSocket, Depends
from app.auth import get_current_user_ws

@app.websocket("/ws/video-stream")
async def websocket_endpoint(
    websocket: WebSocket,
    current_user: User = Depends(get_current_user_ws)
):
    # Authenticate WebSocket connection
    if not current_user:
        await websocket.close(code=1008, reason="Unauthorized")
        return
    
    await manager.connect(websocket)
    # ... rest of the logic
```

### Rate Limiting
```python
# Rate limiting for WebSocket
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.websocket("/ws/video-stream")
@limiter.limit("10/second")
async def websocket_endpoint(websocket: WebSocket):
    # ... WebSocket logic
```

## Monitoring and Analytics

### WebSocket Metrics
```python
# WebSocket metrics
class WebSocketMetrics:
    def __init__(self):
        self.connections_count = 0
        self.messages_sent = 0
        self.messages_received = 0
        self.errors_count = 0
    
    def increment_connections(self):
        self.connections_count += 1
    
    def decrement_connections(self):
        self.connections_count -= 1
    
    def increment_messages_sent(self):
        self.messages_sent += 1
    
    def increment_messages_received(self):
        self.messages_received += 1
    
    def increment_errors(self):
        self.errors_count += 1
    
    def get_metrics(self):
        return {
            "connections": self.connections_count,
            "messages_sent": self.messages_sent,
            "messages_received": self.messages_received,
            "errors": self.errors_count
        }

metrics = WebSocketMetrics()
```

### Performance Monitoring
```typescript
// Performance monitoring
class PerformanceMonitor {
  private frameTimes: number[] = [];
  private maxSamples: number = 100;
  
  startFrame(): number {
    return performance.now();
  }
  
  endFrame(startTime: number): void {
    const frameTime = performance.now() - startTime;
    this.frameTimes.push(frameTime);
    
    if (this.frameTimes.length > this.maxSamples) {
      this.frameTimes.shift();
    }
  }
  
  getAverageFrameTime(): number {
    if (this.frameTimes.length === 0) return 0;
    return this.frameTimes.reduce((a, b) => a + b, 0) / this.frameTimes.length;
  }
  
  getFPS(): number {
    const avgFrameTime = this.getAverageFrameTime();
    return avgFrameTime > 0 ? 1000 / avgFrameTime : 0;
  }
}
```
