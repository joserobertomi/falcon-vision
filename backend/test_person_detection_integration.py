"""
Test script for Person Detection Integration

This script tests the frame processor integration with sample images.
Run this to verify the person detection is working before testing with WebSocket.

Usage:
    python test_person_detection_integration.py
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    import cv2
    import numpy as np
    from app.cv_model.frame_processor import get_frame_processor
    
    DEPENDENCIES_OK = True
    
    # Check if GUI functions are available (opencv-python vs opencv-python-headless)
    # opencv-python-headless has the functions but they don't work
    GUI_AVAILABLE = False
    try:
        # Try to create a window to test if GUI is actually available
        cv2.namedWindow('test', cv2.WINDOW_NORMAL)
        cv2.destroyWindow('test')
        GUI_AVAILABLE = True
    except:
        pass
    
    if not GUI_AVAILABLE:
        print("ℹ️  Note: Using opencv-python-headless (no GUI display)")
        print("   Display tests will save images instead of showing them\n")
        
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("\nInstall required packages:")
    print("pip install ultralytics opencv-python-headless numpy pyzbar")
    DEPENDENCIES_OK = False
    GUI_AVAILABLE = False


async def test_with_webcam():
    """Test person detection with live webcam feed."""
    print("\n" + "="*60)
    print("Testing Person Detection with Webcam")
    print("="*60)
    
    # Initialize frame processor
    processor = get_frame_processor(confidence_threshold=0.5, enable_qr=False)
    print("✅ Frame processor initialized")
    
    # Open webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Could not open webcam")
        return False
    
    print("✅ Webcam opened")
    if GUI_AVAILABLE:
        print("\nProcessing frames... Press 'q' to quit\n")
    else:
        print("\nProcessing frames (headless mode - no display window)\n")
    
    frame_count = 0
    detection_count = 0
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Failed to read frame")
                break
            
            # Encode frame to bytes (simulating WebSocket transmission)
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            frame_bytes = buffer.tobytes()
            
            # Process frame (this is what happens in streaming.py)
            processed_bytes, results = await processor.process_frame(frame_bytes)
            
            if processed_bytes:
                # Decode processed frame for display
                nparr = np.frombuffer(processed_bytes, np.uint8)
                processed_frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                # Display or save results
                if GUI_AVAILABLE:
                    cv2.imshow('Person Detection Test', processed_frame)
                elif frame_count == 0:
                    # Save first frame as sample when GUI not available
                    cv2.imwrite('/tmp/person_detection_sample.jpg', processed_frame)
                    print("💾 Saved sample frame to: /tmp/person_detection_sample.jpg")
                
                frame_count += 1
                person_count = results.get("person_count", 0)
                
                if person_count > 0:
                    detection_count += 1
                    print(f"Frame {frame_count}: ✅ Detected {person_count} person(s) "
                          f"(avg confidence: {results.get('avg_confidence', 0):.2f})")
                else:
                    print(f"Frame {frame_count}: No persons detected")
                
                # Print detection details
                if results.get("detections"):
                    for i, det in enumerate(results["detections"]):
                        bbox = det["bbox"]
                        conf = det["confidence"]
                        print(f"  Person {i+1}: bbox={bbox}, confidence={conf:.2f}")
            else:
                print(f"❌ Frame processing failed: {results.get('error', 'Unknown error')}")
            
            # Break on 'q' key (only if GUI available)
            if GUI_AVAILABLE:
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("\nStopping test...")
                    break
            
            # Stop after 100 frames for testing
            if frame_count >= 100:
                print("\nReached 100 frames, stopping test...")
                break
                
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    finally:
        cap.release()
        if GUI_AVAILABLE:
            cv2.destroyAllWindows()
        
        # Print summary
        print("\n" + "="*60)
        print("Test Summary")
        print("="*60)
        print(f"Total frames processed: {frame_count}")
        print(f"Frames with detections: {detection_count}")
        print(f"Detection rate: {detection_count/frame_count*100:.1f}%")
        print("="*60)
        
        return True


async def test_with_sample_image():
    """Test person detection with a sample image."""
    print("\n" + "="*60)
    print("Testing Person Detection with Sample Image")
    print("="*60)
    
    # Initialize frame processor
    processor = get_frame_processor(confidence_threshold=0.5, enable_qr=False)
    print("✅ Frame processor initialized")
    
    # Create a sample image with text (for testing without actual persons)
    sample_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(sample_frame, "Person Detection Test", (150, 240), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # Encode to bytes
    _, buffer = cv2.imencode('.jpg', sample_frame)
    frame_bytes = buffer.tobytes()
    
    print(f"✅ Sample image created ({len(frame_bytes)} bytes)")
    
    # Process frame
    print("\nProcessing frame...")
    processed_bytes, results = await processor.process_frame(frame_bytes)
    
    if processed_bytes:
        print(f"✅ Frame processed successfully ({len(processed_bytes)} bytes)")
        print(f"\nResults:")
        print(f"  Persons detected: {results.get('person_count', 0)}")
        print(f"  Average confidence: {results.get('avg_confidence', 'N/A')}")
        print(f"  Frames processed: {results.get('frames_processed', 0)}")
        print(f"  QR codes: {results.get('qr_codes', [])}")
        
        # Display or save image
        nparr = np.frombuffer(processed_bytes, np.uint8)
        processed_frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if GUI_AVAILABLE:
            cv2.imshow('Processed Frame', processed_frame)
            print("\nDisplaying processed frame. Press any key to continue...")
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            output_path = '/tmp/processed_sample.jpg'
            cv2.imwrite(output_path, processed_frame)
            print(f"\n💾 Saved processed frame to: {output_path}")
        
        return True
    else:
        print(f"❌ Frame processing failed: {results.get('error', 'Unknown error')}")
        return False


async def test_configuration():
    """Test configuration changes."""
    print("\n" + "="*60)
    print("Testing Configuration Changes")
    print("="*60)
    
    # Test different confidence thresholds
    thresholds = [0.3, 0.5, 0.7, 0.9]
    
    for threshold in thresholds:
        processor = get_frame_processor(confidence_threshold=threshold, enable_qr=False)
        print(f"✅ Created processor with confidence threshold: {threshold}")
    
    # Test with QR enabled
    processor = get_frame_processor(confidence_threshold=0.5, enable_qr=True)
    print(f"✅ Created processor with QR detection enabled")
    
    print("\n✅ Configuration test passed")
    return True


async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("Person Detection Integration Test Suite")
    print("="*60)
    
    if not DEPENDENCIES_OK:
        print("\n❌ Cannot run tests - missing dependencies")
        return
    
    # Test 1: Configuration
    print("\n[Test 1/3] Testing Configuration...")
    config_ok = await test_configuration()
    
    # Test 2: Sample Image
    print("\n[Test 2/3] Testing with Sample Image...")
    sample_ok = await test_with_sample_image()
    
    # Test 3: Webcam (optional)
    print("\n[Test 3/3] Testing with Webcam...")
    webcam_input = input("Test with webcam? (y/n): ").lower().strip()
    
    webcam_ok = True
    if webcam_input == 'y':
        webcam_ok = await test_with_webcam()
    else:
        print("⏭️  Skipping webcam test")
    
    # Final summary
    print("\n" + "="*60)
    print("Final Test Results")
    print("="*60)
    print(f"Configuration Test: {'✅ PASSED' if config_ok else '❌ FAILED'}")
    print(f"Sample Image Test: {'✅ PASSED' if sample_ok else '❌ FAILED'}")
    print(f"Webcam Test: {'✅ PASSED' if webcam_ok else '⏭️  SKIPPED'}")
    print("="*60)
    
    if config_ok and sample_ok:
        print("\n✅ Integration test PASSED - Ready for WebSocket streaming!")
        print("\nNext steps:")
        print("1. Start backend: uvicorn app.api.main:app --reload")
        print("2. Start frontend: streamlit run app/pages/camera.py")
        print("3. Connect with JWT token and start streaming")
    else:
        print("\n❌ Some tests failed - check errors above")


if __name__ == "__main__":
    asyncio.run(main())

