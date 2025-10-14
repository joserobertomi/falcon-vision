import cv2
import numpy as np
import mediapipe as mp
import time
from typing import Tuple, List, Optional


class MediaPipePersonTracker:
    def __init__(self, camera_index=0, confidence_threshold=0.5):
        """
        Initialize the person tracker with MediaPipe.
        
        Args:
            camera_index (int): Camera device index (usually 0 for default camera)
            confidence_threshold (float): Minimum confidence for person detection
        """
        self.camera_index = camera_index
        self.confidence_threshold = confidence_threshold
        self.cap = None
        
        # Initialize MediaPipe solutions
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Initialize pose detection
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=confidence_threshold,
            min_tracking_confidence=0.5
        )
        
        # Initialize object detection for person detection
        self.mp_objectron = mp.solutions.objectron
        self.objectron = self.mp_objectron.Objectron(
            static_image_mode=False,
            max_num_objects=5,
            min_detection_confidence=confidence_threshold,
            min_tracking_confidence=0.5
        )
        
        print("MediaPipe Person Tracker initialized successfully!")
    
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
    
    def detect_persons(self, frame) -> Tuple[np.ndarray, int]:
        """
        Detect persons in the frame using MediaPipe Objectron.
        
        Args:
            frame: Input frame from camera
            
        Returns:
            tuple: (frame_with_detections, person_count)
        """
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        results = self.objectron.process(rgb_frame)
        
        person_count = 0
        annotated_frame = frame.copy()
        
        if results.detected_objects:
            for detected_object in results.detected_objects:
                # Draw 3D bounding box
                self.mp_drawing.draw_landmarks(
                    annotated_frame,
                    detected_object.landmarks_2d,
                    self.mp_objectron.BOX_CONNECTIONS
                )
                person_count += 1
        
        return annotated_frame, person_count
    
    def detect_pose(self, frame) -> Tuple[np.ndarray, int]:
        """
        Detect human pose in the frame using MediaPipe Pose.
        
        Args:
            frame: Input frame from camera
            
        Returns:
            tuple: (frame_with_pose, pose_count)
        """
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        results = self.pose.process(rgb_frame)
        
        annotated_frame = frame.copy()
        pose_count = 0
        
        if results.pose_landmarks:
            # Draw pose landmarks
            self.mp_drawing.draw_landmarks(
                annotated_frame,
                results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
            )
            pose_count = 1
        
        return annotated_frame, pose_count
    
    def process_frame(self, frame) -> Tuple[np.ndarray, int, int]:
        """
        Process a single frame for person detection and pose estimation.
        
        Args:
            frame: Input frame from camera
            
        Returns:
            tuple: (processed_frame, person_count, pose_count)
        """
        try:
            # Detect persons using objectron
            frame_with_persons, person_count = self.detect_persons(frame)
            
            # Detect pose landmarks
            frame_with_pose, pose_count = self.detect_pose(frame)
            
            # Combine both detections
            # Overlay pose on the person detection frame
            if pose_count > 0:
                # Convert BGR to RGB for pose detection
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.pose.process(rgb_frame)
                
                if results.pose_landmarks:
                    self.mp_drawing.draw_landmarks(
                        frame_with_persons,
                        results.pose_landmarks,
                        self.mp_pose.POSE_CONNECTIONS,
                        landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
                    )
            
            return frame_with_persons, person_count, pose_count
            
        except Exception as e:
            print(f"Error processing frame: {e}")
            return frame, 0, 0
    
    def draw_info_overlay(self, frame, person_count, pose_count, fps):
        """
        Draw information overlay on the frame.
        
        Args:
            frame: Frame to draw on
            person_count: Number of persons detected
            pose_count: Number of poses detected
            fps: Current FPS
        """
        # Background rectangle for text
        cv2.rectangle(frame, (10, 10), (300, 120), (0, 0, 0), -1)
        cv2.rectangle(frame, (10, 10), (300, 120), (255, 255, 255), 2)
        
        # Add text information
        cv2.putText(frame, f"Persons detected: {person_count}", (20, 35), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Poses detected: {pose_count}", (20, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(frame, f"FPS: {fps:.1f}", (20, 85), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        cv2.putText(frame, "Press 'q' to quit, 's' to save", (20, 110), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    def run_tracking(self):
        """Main tracking loop."""
        try:
            self.start_camera()
            
            print("Starting person tracking with MediaPipe...")
            print("Press 'q' to quit, 's' to save current frame")
            print("Press 'p' to toggle pose detection, 'o' to toggle object detection")
            
            frame_count = 0
            start_time = time.time()
            show_pose = True
            show_objects = True
            
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("Failed to read frame from camera")
                    break
                
                # Process the frame based on current settings
                if show_objects and show_pose:
                    processed_frame, person_count, pose_count = self.process_frame(frame)
                elif show_objects:
                    processed_frame, person_count, pose_count = self.detect_persons(frame)
                    pose_count = 0
                elif show_pose:
                    processed_frame, person_count, pose_count = self.detect_pose(frame)
                    person_count = 0
                else:
                    processed_frame = frame
                    person_count = pose_count = 0
                
                # Calculate FPS
                frame_count += 1
                if frame_count % 30 == 0:  # Update FPS every 30 frames
                    elapsed_time = time.time() - start_time
                    fps = frame_count / elapsed_time
                else:
                    fps = 0
                
                # Add information overlay
                self.draw_info_overlay(processed_frame, person_count, pose_count, fps)
                
                # Add mode indicators
                mode_text = f"Objects: {'ON' if show_objects else 'OFF'} | Pose: {'ON' if show_pose else 'OFF'}"
                cv2.putText(processed_frame, mode_text, (10, frame.shape[0] - 20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                # Display the frame
                cv2.imshow('MediaPipe Person Tracking', processed_frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    # Save current frame
                    filename = f"mediapipe_tracking_frame_{int(time.time())}.jpg"
                    cv2.imwrite(filename, processed_frame)
                    print(f"Frame saved as {filename}")
                elif key == ord('p'):
                    show_pose = not show_pose
                    print(f"Pose detection: {'ON' if show_pose else 'OFF'}")
                elif key == ord('o'):
                    show_objects = not show_objects
                    print(f"Object detection: {'ON' if show_objects else 'OFF'}")
                
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
    print("MediaPipe Person Tracking Application")
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
