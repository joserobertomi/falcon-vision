#!/usr/bin/env python3
"""
Test script for the person tracking application.
This script can be used to test the application without running the full GUI.
"""

import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

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
        from ikomia.dataprocess.workflow import Workflow
        print("✓ Ikomia Workflow imported successfully")
    except ImportError as e:
        print(f"✗ Ikomia import failed: {e}")
        return False
    
    try:
        from app.main import PersonTracker
        print("✓ PersonTracker class imported successfully")
    except ImportError as e:
        print(f"✗ PersonTracker import failed: {e}")
        return False
    
    return True

def test_camera_availability():
    """Test if a camera is available."""
    print("\nTesting camera availability...")
    
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print("✓ Camera is available and working")
                cap.release()
                return True
            else:
                print("✗ Camera opened but cannot read frames")
                cap.release()
                return False
        else:
            print("✗ Camera could not be opened")
            return False
            
    except Exception as e:
        print(f"✗ Camera test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Person Tracking Application - Test Suite")
    print("=" * 45)
    
    # Test imports
    imports_ok = test_imports()
    
    # Test camera
    camera_ok = test_camera_availability()
    
    print("\n" + "=" * 45)
    print("Test Results:")
    print(f"Imports: {'PASS' if imports_ok else 'FAIL'}")
    print(f"Camera:  {'PASS' if camera_ok else 'FAIL'}")
    
    if imports_ok and camera_ok:
        print("\n✓ All tests passed! You can run the application with:")
        print("  python app/main.py")
    else:
        print("\n✗ Some tests failed. Please check the installation:")
        if not imports_ok:
            print("  - Install missing dependencies: pip install ikomia opencv-python numpy pillow")
        if not camera_ok:
            print("  - Check camera connection and permissions")

if __name__ == "__main__":
    main()
