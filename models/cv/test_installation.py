#!/usr/bin/env python3
"""
Test script to verify MediaPipe installation and basic functionality
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported."""
    print("Testing imports...")
    
    try:
        import cv2
        print("✓ OpenCV imported successfully")
    except ImportError as e:
        print(f"✗ OpenCV import failed: {e}")
        return False
    
    try:
        import numpy as np
        print("✓ NumPy imported successfully")
    except ImportError as e:
        print(f"✗ NumPy import failed: {e}")
        return False
    
    try:
        import mediapipe as mp
        print("✓ MediaPipe imported successfully")
    except ImportError as e:
        print(f"✗ MediaPipe import failed: {e}")
        return False
    
    try:
        from PIL import Image
        print("✓ Pillow imported successfully")
    except ImportError as e:
        print(f"✗ Pillow import failed: {e}")
        return False
    
    return True

def test_mediapipe_initialization():
    """Test MediaPipe solutions initialization."""
    print("\nTesting MediaPipe initialization...")
    
    try:
        import mediapipe as mp
        
        # Test pose solution
        mp_pose = mp.solutions.pose
        pose = mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        print("✓ MediaPipe Pose initialized successfully")
        
        # Test objectron solution
        mp_objectron = mp.solutions.objectron
        objectron = mp_objectron.Objectron(
            static_image_mode=False,
            max_num_objects=5,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        print("✓ MediaPipe Objectron initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ MediaPipe initialization failed: {e}")
        return False

def test_camera_access():
    """Test camera access."""
    print("\nTesting camera access...")
    
    try:
        import cv2
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("✗ Camera not accessible (camera index 0)")
            return False
        
        ret, frame = cap.read()
        if not ret:
            print("✗ Failed to read from camera")
            cap.release()
            return False
        
        print(f"✓ Camera accessible, frame size: {frame.shape}")
        cap.release()
        return True
        
    except Exception as e:
        print(f"✗ Camera test failed: {e}")
        return False

def test_tracker_import():
    """Test if the tracker module can be imported."""
    print("\nTesting tracker module import...")
    
    try:
        # Add app directory to path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))
        
        from mediapipe_tracker import MediaPipePersonTracker
        print("✓ MediaPipePersonTracker imported successfully")
        
        # Test instantiation (without camera)
        tracker = MediaPipePersonTracker(camera_index=0, confidence_threshold=0.5)
        print("✓ MediaPipePersonTracker instantiated successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Tracker import failed: {e}")
        return False

def main():
    """Run all tests."""
    print("MediaPipe Person Tracker - Installation Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_mediapipe_initialization,
        test_camera_access,
        test_tracker_import
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! The application should work correctly.")
        print("\nTo run the tracker:")
        print("  python run_tracker.py")
    else:
        print("✗ Some tests failed. Please check the installation.")
        print("\nInstallation commands:")
        print("  pip install mediapipe opencv-python numpy pillow")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
