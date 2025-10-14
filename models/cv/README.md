# MediaPipe Person Tracking Application

A real-time person tracking application using MediaPipe for computer vision tasks. This application provides both person detection and human pose estimation capabilities.

## Features

- **Real-time Person Detection**: Uses MediaPipe Objectron for detecting persons in the camera feed
- **Human Pose Estimation**: Uses MediaPipe Pose for detecting and tracking human pose landmarks
- **Interactive Controls**: Toggle between different detection modes during runtime
- **Performance Monitoring**: Real-time FPS display
- **Frame Saving**: Save current frames as images
- **Configurable Confidence**: Adjustable detection confidence thresholds

## Installation

1. **Install Dependencies**:
   ```bash
   # Install using pip
   pip install mediapipe opencv-python numpy pillow
   
   # Or install from pyproject.toml
   pip install -e .
   ```

2. **Camera Setup**:
   - Ensure your camera is connected and accessible
   - Grant camera permissions if required by your system

## Usage

### Quick Start

```bash
# Run the application
python run_tracker.py

# Or run directly from the app directory
cd app
python main.py
```

### Controls

- **'q'**: Quit the application
- **'s'**: Save current frame as an image
- **'p'**: Toggle pose detection on/off
- **'o'**: Toggle object detection on/off

### Configuration

You can modify the tracking parameters in `main.py`:

```python
tracker = MediaPipePersonTracker(
    camera_index=0,           # Camera device index
    confidence_threshold=0.5  # Detection confidence threshold (0.0-1.0)
)
```

## Application Structure

```
models/cv/
├── app/
│   ├── main.py                 # Main application entry point
│   └── mediapipe_tracker.py    # MediaPipe tracker implementation
├── run_tracker.py              # Simple launcher script
├── pyproject.toml              # Project dependencies
└── README.md                   # This file
```

## Technical Details

### MediaPipe Solutions Used

1. **Objectron**: For person detection and 3D bounding box estimation
2. **Pose**: For human pose landmark detection and tracking

### Performance

- Optimized for real-time performance
- Configurable model complexity
- Efficient frame processing pipeline
- FPS monitoring and display

### Requirements

- Python 3.10+
- MediaPipe
- OpenCV
- NumPy
- Pillow
- Camera device

## Troubleshooting

### Common Issues

1. **Camera not found**:
   - Check if camera is connected
   - Try different camera indices (0, 1, 2, etc.)
   - Ensure camera permissions are granted

2. **Low FPS**:
   - Reduce camera resolution in the code
   - Lower the confidence threshold
   - Close other applications using the camera

3. **Installation issues**:
   - Ensure Python 3.10+ is installed
   - Use a virtual environment
   - Check MediaPipe installation: `pip show mediapipe`

### Debug Mode

To run with verbose output, modify the confidence threshold or add debug prints in the tracker class.

## License

This project is part of the Falcon Vision system.