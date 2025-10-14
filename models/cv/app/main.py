"""
Person Tracking Application using MediaPipe

This application uses MediaPipe for real-time person detection and pose estimation.
It provides both object detection and pose landmark detection capabilities.

Features:
- Real-time person detection using MediaPipe Objectron
- Human pose estimation using MediaPipe Pose
- Interactive controls for toggling detection modes
- FPS monitoring and frame saving
- Configurable confidence thresholds

Controls:
- 'q': Quit the application
- 's': Save current frame
- 'p': Toggle pose detection
- 'o': Toggle object detection
"""

from mediapipe_tracker import MediaPipePersonTracker


def main():
    """Main function to run the person tracking application."""
    print("MediaPipe Person Tracking Application")
    print("=" * 40)
    print("Features:")
    print("- Real-time person detection")
    print("- Human pose estimation")
    print("- Interactive controls")
    print("=" * 40)
    
    try:
        # Create tracker instance
        tracker = MediaPipePersonTracker(camera_index=0, confidence_threshold=0.5)
        
        # Start tracking
        tracker.run_tracking()
        
    except Exception as e:
        print(f"Application error: {e}")
        print("Make sure you have:")
        print("1. A camera connected to your system")
        print("2. MediaPipe properly installed")
        print("3. Required dependencies installed")
        print("4. Camera permissions granted")


if __name__ == "__main__":
    main()
