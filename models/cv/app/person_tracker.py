import cv2
import numpy as np
import time
from typing import Tuple, List, Optional
from ultralytics import YOLO
from pyzbar import pyzbar


class PersonDetector:
    def __init__(self, camera_index=0, confidence_threshold=0.5):
        """
        Initialize the person detector with YOLOv8.
        
        Args:
            camera_index (int): Camera device index (usually 0 for default camera)
            confidence_threshold (float): Minimum confidence for person detection
        """
        self.camera_index = camera_index
        self.confidence_threshold = confidence_threshold
        self.cap = None
        
        # Initialize YOLOv8 model (nano version for speed)
        print("Loading YOLOv8 model...")
        self.model = YOLO('yolov8n.pt')  # 'n' = nano (fastest), 's' = small, 'm' = medium
        
        # COCO dataset class for person is 0
        self.person_class_id = 0
        
        print("Person Detector initialized successfully!")
    
    def start_camera(self):
        """Initialize camera capture."""
        self.cap = cv2.VideoCapture(self.camera_index)
        
        if not self.cap.isOpened():
            raise RuntimeError(f"Could not open camera {self.camera_index}")
        
        # Set camera properties for better performance
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        print(f"Camera {self.camera_index} initialized successfully!")
    
    def detect_qr_codes(self, frame) -> Tuple[np.ndarray, List[str]]:
        """
        Detect QR codes in the frame.
        
        Args:
            frame: Input frame from camera
            
        Returns:
            tuple: (frame_with_qr_detections, qr_data_list)
        """
        # Convert frame to grayscale for QR code detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect QR codes
        qr_codes = pyzbar.decode(gray)
        
        qr_data_list = []
        annotated_frame = frame.copy()
        
        for qr_code in qr_codes:
            # Extract QR code data
            qr_data = qr_code.data.decode('utf-8')
            qr_data_list.append(qr_data)
            
            # Get QR code location
            rect = qr_code.rect
            x, y, w, h = rect.left, rect.top, rect.width, rect.height
            
            # Draw rectangle around QR code
            cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            
            # Draw QR code data as text
            cv2.putText(annotated_frame, qr_data, (x, y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        
        return annotated_frame, qr_data_list

    def detect_persons(self, frame) -> Tuple[np.ndarray, int, List]:
        """
        Detect persons in the frame using YOLOv8.
        
        Args:
            frame: Input frame from camera
            
        Returns:
            tuple: (frame_with_detections, person_count, detections_info)
        """
        # Run YOLOv8 inference
        results = self.model(frame, verbose=False)
        
        person_count = 0
        detections_info = []
        annotated_frame = frame.copy()
        
        # Process results
        for result in results:
            boxes = result.boxes
            
            for box in boxes:
                # Get class id and confidence
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                
                # Check if it's a person and meets confidence threshold
                if class_id == self.person_class_id and confidence >= self.confidence_threshold:
                    # Get bounding box coordinates
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    
                    # Draw bounding box
                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    
                    # Draw label with confidence
                    label = f'Person {confidence:.2f}'
                    label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                    
                    # Draw label background
                    cv2.rectangle(annotated_frame, 
                                (x1, y1 - label_size[1] - 10), 
                                (x1 + label_size[0], y1), 
                                (0, 255, 0), -1)
                    
                    # Draw label text
                    cv2.putText(annotated_frame, label, (x1, y1 - 5), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
                    
                    person_count += 1
                    detections_info.append({
                        'bbox': (x1, y1, x2, y2),
                        'confidence': confidence
                    })
        
        return annotated_frame, person_count, detections_info
    
    def draw_info_overlay(self, frame, person_count, fps, avg_confidence=None, qr_count=0):
        """
        Draw information overlay on the frame.
        
        Args:
            frame: Frame to draw on
            person_count: Number of persons detected
            fps: Current FPS
            avg_confidence: Average confidence of detections
            qr_count: Number of QR codes detected
        """
        # Background rectangle for text
        overlay_height = 160 if avg_confidence else 140
        cv2.rectangle(frame, (10, 10), (300, overlay_height), (0, 0, 0), -1)
        cv2.rectangle(frame, (10, 10), (300, overlay_height), (255, 255, 255), 2)
        
        # Add text information
        cv2.putText(frame, f"Persons detected: {person_count}", (20, 35), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"QR codes detected: {qr_count}", (20, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        cv2.putText(frame, f"FPS: {fps:.1f}", (20, 85), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        
        if avg_confidence is not None:
            cv2.putText(frame, f"Avg Confidence: {avg_confidence:.2f}", (20, 110), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            y_pos = 135
        else:
            y_pos = 110
        
        cv2.putText(frame, "Press 'q' to quit, 's' to save", (20, y_pos), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    def run_detection(self):
        """Main detection loop."""
        try:
            self.start_camera()
            
            print("\nStarting person detection with YOLOv8...")
            print("=" * 50)
            print("Controls:")
            print("  'q' - Quit the application")
            print("  's' - Save current frame")
            print("  QR code with 'exit' - Quit the application")
            print("=" * 50)
            
            frame_count = 0
            start_time = time.time()
            fps = 0
            
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("Failed to read frame from camera")
                    break
                
                # Detect QR codes first
                qr_frame, qr_data_list = self.detect_qr_codes(frame)
                
                # Check for exit QR code
                if "exit" in qr_data_list:
                    print("\nExit QR code detected! Quitting application...")
                    break
                
                # Detect persons in the frame
                processed_frame, person_count, detections_info = self.detect_persons(qr_frame)
                
                # Calculate average confidence
                avg_confidence = None
                if detections_info:
                    avg_confidence = sum(d['confidence'] for d in detections_info) / len(detections_info)
                
                # Calculate FPS
                frame_count += 1
                if frame_count % 30 == 0:  # Update FPS every 30 frames
                    elapsed_time = time.time() - start_time
                    fps = frame_count / elapsed_time
                
                # Add information overlay
                self.draw_info_overlay(processed_frame, person_count, fps, avg_confidence, len(qr_data_list))
                
                # Display the frame
                cv2.imshow('YOLOv8 Person Detection', processed_frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("\nQuitting application...")
                    break
                elif key == ord('s'):
                    # Save current frame
                    filename = f"person_detection_frame_{int(time.time())}.jpg"
                    cv2.imwrite(filename, processed_frame)
                    print(f"Frame saved as {filename}")
                
        except KeyboardInterrupt:
            print("\nDetection stopped by user")
        except Exception as e:
            print(f"Error during detection: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("Cleanup completed")


def main():
    """Main function to run the person detection application."""
    print("=" * 50)
    print("YOLOv8 Person Detection Application")
    print("=" * 50)
    print("\nInitializing...")
    
    try:
        # Create detector instance
        detector = PersonDetector(camera_index=0, confidence_threshold=0.5)
        
        # Start detection
        detector.run_detection()
        
    except Exception as e:
        print(f"\nApplication error: {e}")
        print("\nTroubleshooting:")
        print("1. Install required packages:")
        print("   pip install ultralytics opencv-python")
        print("2. Make sure you have a camera connected")
        print("3. Grant camera permissions to Python")
        print("4. Check if another application is using the camera")


if __name__ == "__main__":
    main()