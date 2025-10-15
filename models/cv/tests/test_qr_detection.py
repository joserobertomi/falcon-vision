#!/usr/bin/env python3
"""
Test script to verify QR code detection functionality.
This script tests the QR code detection on the generated exit QR code image.
"""

import cv2
import numpy as np
from pyzbar import pyzbar
import os

def test_qr_detection(image_path):
    """Test QR code detection on an image file."""
    if not os.path.exists(image_path):
        print(f"Error: Image file '{image_path}' not found!")
        return False
    
    # Read the image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not read image '{image_path}'!")
        return False
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Detect QR codes
    qr_codes = pyzbar.decode(gray)
    
    print(f"Testing QR code detection on: {image_path}")
    print(f"Found {len(qr_codes)} QR code(s)")
    
    for i, qr_code in enumerate(qr_codes):
        qr_data = qr_code.data.decode('utf-8')
        print(f"QR Code {i+1}: '{qr_data}'")
        
        if qr_data == "exit":
            print("[SUCCESS] Exit QR code detected successfully!")
            return True
    
    if len(qr_codes) == 0:
        print("[ERROR] No QR codes detected!")
        return False
    else:
        print("[ERROR] Exit QR code not found!")
        return False

def main():
    """Main function to test QR code detection."""
    print("QR Code Detection Test")
    print("=" * 30)
    
    # Test with the generated exit QR code
    exit_qr_path = "exit_qr_code.png"
    
    if test_qr_detection(exit_qr_path):
        print("\n[SUCCESS] QR code detection test PASSED!")
        print("The exit functionality should work correctly in the applications.")
    else:
        print("\n[ERROR] QR code detection test FAILED!")
        print("There might be an issue with the QR code detection setup.")

if __name__ == "__main__":
    main()
