# Computer Vision Architecture

## Overview

The Falcon Vision computer vision system is built around YOLOv8 for real-time person detection, providing accurate and efficient detection capabilities for video streams.

## Technology Stack

- **Detection Model**: YOLOv8 (You Only Look Once)
- **Computer Vision**: OpenCV
- **Image Processing**: NumPy, PIL
- **Model Management**: Ultralytics
- **QR Code Detection**: PyZbar

## Core Components

### Detection Pipeline

1. **Video Input**: WebSocket video stream or file input
2. **Frame Processing**: Frame extraction and preprocessing
3. **Model Inference**: YOLOv8 person detection
4. **Post-processing**: NMS, confidence filtering
5. **Output**: Bounding boxes and confidence scores

### Model Architecture

#### YOLOv8 Configuration
- **Input Size**: 640x640 pixels
- **Classes**: Person detection (class 0)
- **Confidence Threshold**: 0.5
- **NMS Threshold**: 0.45
- **Model Format**: ONNX for optimization

#### Performance Metrics
- **Inference Speed**: ~30 FPS on GPU
- **Accuracy**: mAP@0.5 > 0.8
- **Memory Usage**: ~2GB VRAM
- **Model Size**: ~25MB

## Detection Service

### DetectionService Class
```python
class DetectionService:
    def __init__(self):
        self.model = YOLO('yolov8n.pt')
        self.confidence_threshold = 0.5
    
    async def detect_persons(self, frame: np.ndarray) -> List[Detection]:
        # Model inference and post-processing
        pass
```

### Key Methods
- **detect_persons()**: Main detection function
- **preprocess_frame()**: Image preprocessing
- **postprocess_detections()**: NMS and filtering
- **calculate_metrics()**: Performance metrics

## Video Processing

### Frame Processing Pipeline
1. **Frame Capture**: Extract frames from video stream
2. **Resize**: Scale to model input size
3. **Normalization**: Pixel value normalization
4. **Inference**: Run YOLOv8 model
5. **Post-processing**: Apply NMS and filtering

### Real-time Processing
- **Async Processing**: Non-blocking detection
- **Frame Skipping**: Adaptive frame rate
- **Buffer Management**: Efficient memory usage
- **Error Handling**: Graceful failure recovery

## Data Structures

### Detection Object
```python
@dataclass
class Detection:
    bbox: BoundingBox
    confidence: float
    class_id: int
    timestamp: datetime
    frame_id: int
```

### BoundingBox
```python
@dataclass
class BoundingBox:
    x1: int
    y1: int
    x2: int
    y2: int
    width: int
    height: int
```

## Performance Optimization

### Model Optimization
- **ONNX Conversion**: Faster inference
- **Quantization**: Reduced model size
- **TensorRT**: GPU acceleration
- **Batch Processing**: Multiple frames

### Memory Management
- **Frame Caching**: Efficient memory usage
- **Garbage Collection**: Automatic cleanup
- **Memory Pooling**: Reuse of objects
- **Streaming**: Continuous processing

## Integration Points

### Backend Integration
- **FastAPI Endpoints**: Detection API
- **WebSocket Streaming**: Real-time video
- **Database Storage**: Detection records
- **Analytics**: Performance metrics

### Frontend Integration
- **Real-time Display**: Live detection overlay
- **Analytics Dashboard**: Detection statistics
- **Configuration**: Model parameters
- **Monitoring**: Performance metrics

## Configuration

### Model Parameters
```python
DETECTION_CONFIG = {
    "model_path": "models/yolov8n.pt",
    "confidence_threshold": 0.5,
    "nms_threshold": 0.45,
    "input_size": (640, 640),
    "max_detections": 100
}
```

### Performance Settings
```python
PERFORMANCE_CONFIG = {
    "gpu_enabled": True,
    "batch_size": 1,
    "frame_skip": 1,
    "max_fps": 30
}
```

## Monitoring and Metrics

### Detection Metrics
- **Detection Count**: Persons detected per frame
- **Confidence Scores**: Average confidence
- **Processing Time**: Inference latency
- **Throughput**: Frames per second

### System Metrics
- **GPU Usage**: Memory and compute
- **CPU Usage**: Processing load
- **Memory Usage**: RAM consumption
- **Error Rate**: Detection failures

## Troubleshooting

### Common Issues
- **Low Detection Accuracy**: Adjust confidence threshold
- **Performance Issues**: Optimize model or hardware
- **Memory Leaks**: Check frame processing
- **Model Loading**: Verify model path and format

### Debug Tools
- **Logging**: Detailed operation logs
- **Profiling**: Performance analysis
- **Visualization**: Detection overlay
- **Metrics**: Real-time monitoring
