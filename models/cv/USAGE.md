# MediaPipe Person Tracking - Usage Guide

## Quick Start

### 1. Install Dependencies
```bash
pip install mediapipe opencv-python numpy pillow
```

### 2. Run the Application

#### With Camera (Live Tracking)
```bash
python run_tracker.py
```

#### Demo Mode (No Camera Required)
```bash
# Using synthetic demo image
python app/demo_mode.py

# Using your own image
python app/demo_mode.py path/to/your/image.jpg

# Using your own video
python app/demo_mode.py path/to/your/video.mp4
```

## Controls

- **'q'**: Quit the application
- **'s'**: Save current frame as image
- **'p'**: Toggle pose detection on/off
- **'o'**: Toggle object detection on/off

## Features

### Person Detection
- Uses MediaPipe Objectron for 3D person detection
- Draws 3D bounding boxes around detected persons
- Configurable confidence threshold

### Pose Estimation
- Uses MediaPipe Pose for human pose landmark detection
- Draws pose skeleton with 33 key points
- Real-time pose tracking

### Performance Monitoring
- Real-time FPS display
- Detection count overlay
- Mode indicators

## Configuration

### Camera Settings
```python
tracker = MediaPipePersonTracker(
    camera_index=0,           # Camera device index
    confidence_threshold=0.5  # Detection confidence (0.0-1.0)
)
```

### Model Complexity
You can adjust the pose model complexity in `mediapipe_tracker.py`:
```python
self.pose = self.mp_pose.Pose(
    model_complexity=1,  # 0, 1, or 2 (higher = more accurate, slower)
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)
```

## Troubleshooting

### No Camera Detected
- Use demo mode: `python app/demo_mode.py`
- Check camera permissions
- Try different camera indices (0, 1, 2, etc.)

### Low Performance
- Reduce model complexity
- Lower confidence threshold
- Reduce camera resolution
- Close other applications

### Installation Issues
- Ensure Python 3.10+ is installed
- Use virtual environment
- Check MediaPipe installation: `pip show mediapipe`

## File Structure

```
models/cv/
├── app/
│   ├── main.py                 # Main application (camera mode)
│   ├── mediapipe_tracker.py    # Core tracker implementation
│   └── demo_mode.py            # Demo mode (no camera)
├── run_tracker.py              # Simple launcher
├── test_installation.py        # Installation test
├── test_demo.py                # Demo functionality test
├── pyproject.toml              # Dependencies
├── README.md                   # Full documentation
└── USAGE.md                    # This file
```

## Examples

### Basic Usage
```python
from app.mediapipe_tracker import MediaPipePersonTracker

# Create tracker
tracker = MediaPipePersonTracker(camera_index=0, confidence_threshold=0.5)

# Start tracking
tracker.run_tracking()
```

### Custom Processing
```python
import cv2
from app.mediapipe_tracker import MediaPipePersonTracker

tracker = MediaPipePersonTracker()

# Process a single frame
frame = cv2.imread("image.jpg")
processed_frame, person_count, pose_count = tracker.process_frame(frame)

# Save result
cv2.imwrite("result.jpg", processed_frame)
```

## Performance Tips

1. **For Real-time**: Use model_complexity=0 or 1
2. **For Accuracy**: Use model_complexity=2
3. **For Speed**: Lower confidence thresholds
4. **For Quality**: Higher confidence thresholds

## Next Steps

- Integrate with your existing computer vision pipeline
- Add custom post-processing
- Implement tracking across frames
- Add custom visualization overlays
