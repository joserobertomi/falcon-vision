# Person Tracking Application with Ikomia

A Python application that uses your camera to track people in real-time using the Ikomia computer vision platform.

## Features

- Real-time person detection and tracking using Ikomia's YOLO v9 algorithm
- Live camera feed with bounding boxes around detected persons
- FPS counter and detection statistics
- Save current frame functionality
- Configurable confidence threshold
- Clean, object-oriented code structure

## Installation

1. Make sure you have Python 3.10+ installed
2. Install the required dependencies:

```bash
pip install ikomia opencv-python numpy pillow
```

Or install from the project:

```bash
pip install -e .
```

## Usage

Run the application:

```bash
python app/main.py
```

### Controls

- **'q'**: Quit the application
- **'s'**: Save the current frame as an image

### Configuration

You can modify the following parameters in the `main()` function:

- `camera_index`: Camera device index (default: 0)
- `confidence_threshold`: Minimum confidence for person detection (default: 0.5)

## Requirements

- A working camera connected to your system
- Ikomia platform access
- Python 3.10 or higher

## Troubleshooting

If you encounter issues:

1. **Camera not found**: Make sure your camera is connected and not being used by another application
2. **Ikomia errors**: Ensure Ikomia is properly installed and you have internet access for model downloads
3. **Performance issues**: Try reducing the input size or confidence threshold in the algorithm parameters

## Algorithm Details

This application uses Ikomia's YOLO v9 algorithm for person detection, which provides:
- High accuracy person detection
- Real-time performance
- Configurable confidence thresholds
- Bounding box visualization

The algorithm is automatically downloaded on first use and cached for subsequent runs.
