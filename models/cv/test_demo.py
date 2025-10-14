#!/usr/bin/env python3
"""
Test script for MediaPipe Person Tracker demo mode
Tests the functionality without requiring a GUI
"""

import sys
import os
import numpy as np
import cv2

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_demo_tracker():
    """Test the demo tracker functionality."""
    print("Testing MediaPipe Demo Person Tracker...")
    
    try:
        from demo_mode import DemoPersonTracker
        
        # Create demo tracker
        tracker = DemoPersonTracker(confidence_threshold=0.5)
        
        # Test synthetic image creation
        print("✓ Creating synthetic demo image...")
        demo_img = tracker.create_synthetic_demo_image()
        print(f"  Image shape: {demo_img.shape}")
        
        # Test frame processing
        print("✓ Testing frame processing...")
        processed_frame, person_count, pose_count = tracker.process_frame(demo_img)
        print(f"  Processed frame shape: {processed_frame.shape}")
        print(f"  Persons detected: {person_count}")
        print(f"  Poses detected: {pose_count}")
        
        # Test info overlay
        print("✓ Testing info overlay...")
        tracker.draw_info_overlay(processed_frame, person_count, pose_count, 30.0)
        
        # Save test result
        output_file = "test_demo_result.jpg"
        cv2.imwrite(output_file, processed_frame)
        print(f"✓ Test result saved as: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"✗ Demo test failed: {e}")
        return False

def test_mediapipe_solutions():
    """Test MediaPipe solutions directly."""
    print("\nTesting MediaPipe solutions directly...")
    
    try:
        import mediapipe as mp
        
        # Test pose solution
        mp_pose = mp.solutions.pose
        pose = mp_pose.Pose(
            static_image_mode=True,
            model_complexity=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Create a test image
        test_img = np.zeros((480, 640, 3), dtype=np.uint8)
        test_img_rgb = cv2.cvtColor(test_img, cv2.COLOR_BGR2RGB)
        
        # Process with pose
        results = pose.process(test_img_rgb)
        print("✓ Pose solution test completed")
        
        # Test objectron solution
        mp_objectron = mp.solutions.objectron
        objectron = mp_objectron.Objectron(
            static_image_mode=True,
            max_num_objects=5,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Process with objectron
        results = objectron.process(test_img_rgb)
        print("✓ Objectron solution test completed")
        
        return True
        
    except Exception as e:
        print(f"✗ MediaPipe solutions test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("MediaPipe Person Tracker - Demo Test")
    print("=" * 40)
    
    tests = [
        test_mediapipe_solutions,
        test_demo_tracker
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! The demo application should work correctly.")
        print("\nTo run the demo:")
        print("  python app/demo_mode.py")
        print("  python app/demo_mode.py path/to/your/image.jpg")
        print("  python app/demo_mode.py path/to/your/video.mp4")
    else:
        print("✗ Some tests failed. Please check the installation.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
