import cv2
import numpy as np
from ikomia.dataprocess.workflow import Workflow
from ikomia.utils.displayIO import display
import time


class PersonTracker:
    def __init__(self, camera_index=0, confidence_threshold=0.5):
        """
        Initialize the person tracker with Ikomia.
        
        Args:
            camera_index (int): Camera device index (usually 0 for default camera)
            confidence_threshold (float): Minimum confidence for person detection
        """
        self.camera_index = camera_index
        self.confidence_threshold = confidence_threshold
        self.workflow = None
        self.detection_algo = None
        self.cap = None
        self.setup_workflow()
    
    def setup_workflow(self):
        """Set up the Ikomia workflow for person detection."""
        try:
            # Initialize the workflow
            self.workflow = Workflow()
            
            # Add YOLO v9 algorithm for person detection
            self.detection_algo = self.workflow.add_task(name="infer_yolo_v9", auto_connect=True)
            
            # Set algorithm parameters
            self.detection_algo.set_parameters({
                "conf_thres": str(self.confidence_threshold),
                "iou_thres": "0.4",
                "input_size": "640"
            })
            
            print("Ikomia workflow initialized successfully!")
            
        except Exception as e:
            print(f"Error setting up Ikomia workflow: {e}")
            raise
    
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
    
    def process_frame(self, frame):
        """
        Process a single frame for person detection.
        
        Args:
            frame: Input frame from camera
            
        Returns:
            tuple: (processed_frame, detection_count)
        """
        try:
            # Run the workflow on the frame
            self.workflow.run_on(image=frame)
            
            # Get the processed image with bounding boxes
            result_img = self.detection_algo.get_image_with_graphics()
            
            # Get detection results
            outputs = self.detection_algo.get_output(0)
            detection_count = 0
            
            if outputs is not None and hasattr(outputs, 'get_objects'):
                objects = outputs.get_objects()
                detection_count = len(objects)
                
                # Print detection info
                for i, obj in enumerate(objects):
                    if hasattr(obj, 'get_class_name') and obj.get_class_name() == 'person':
                        confidence = obj.get_confidence() if hasattr(obj, 'get_confidence') else 0.0
                        print(f"Person {i+1}: Confidence = {confidence:.2f}")
            
            return result_img, detection_count
            
        except Exception as e:
            print(f"Error processing frame: {e}")
            return frame, 0
    
    def run_tracking(self):
        """Main tracking loop."""
        try:
            self.start_camera()
            
            print("Starting person tracking...")
            print("Press 'q' to quit, 's' to save current frame")
            
            frame_count = 0
            start_time = time.time()
            
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("Failed to read frame from camera")
                    break
                
                # Process the frame
                processed_frame, person_count = self.process_frame(frame)
                
                # Add information overlay
                info_text = f"Persons detected: {person_count}"
                cv2.putText(processed_frame, info_text, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # Add FPS counter
                frame_count += 1
                if frame_count % 30 == 0:  # Update FPS every 30 frames
                    elapsed_time = time.time() - start_time
                    fps = frame_count / elapsed_time
                    print(f"FPS: {fps:.1f}")
                
                # Display the frame
                cv2.imshow('Person Tracking - Ikomia', processed_frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    # Save current frame
                    filename = f"person_tracking_frame_{int(time.time())}.jpg"
                    cv2.imwrite(filename, processed_frame)
                    print(f"Frame saved as {filename}")
                
        except KeyboardInterrupt:
            print("\nTracking stopped by user")
        except Exception as e:
            print(f"Error during tracking: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("Cleanup completed")


def main():
    """Main function to run the person tracking application."""
    print("Person Tracking Application using Ikomia")
    print("=" * 40)
    
    try:
        # Create tracker instance
        tracker = PersonTracker(camera_index=0, confidence_threshold=0.5)
        
        # Start tracking
        tracker.run_tracking()
        
    except Exception as e:
        print(f"Application error: {e}")
        print("Make sure you have:")
        print("1. A camera connected to your system")
        print("2. Ikomia properly installed")
        print("3. Required dependencies installed")


if __name__ == "__main__":
    main()
