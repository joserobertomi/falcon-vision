#!/usr/bin/env python3
"""
Demo mode for MediaPipe Person Tracker that works without a camera
Uses a test image or video file instead of live camera feed
"""

import cv2
import numpy as np
import mediapipe as mp
import time
import os
from mediapipe_tracker import MediaPipePersonTracker


class DemoPersonTracker(MediaPipePersonTracker):
    """Extended tracker with demo mode capabilities."""
    
    def __init__(self, demo_source=None, confidence_threshold=0.5):
        """
        Initialize the demo tracker.
        
        Args:
            demo_source: Path to image/video file, or None for synthetic demo
            confidence_threshold: Detection confidence threshold
        """
        # Don't call parent __init__ to avoid camera initialization
        self.demo_source = demo_source
        self.confidence_threshold = confidence_threshold
        self.cap = None
        self.is_video = False
        self.is_image = False
        
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
        
        print("MediaPipe Demo Person Tracker initialized successfully!")
    
    def create_synthetic_demo_image(self):
        """Create a synthetic image with a simple figure for demo purposes."""
        # Create a simple image with a stick figure
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Draw a simple stick figure
        # Head
        cv2.circle(img, (320, 100), 30, (255, 255, 255), -1)
        
        # Body
        cv2.line(img, (320, 130), (320, 300), (255, 255, 255), 5)
        
        # Arms
        cv2.line(img, (320, 150), (250, 200), (255, 255, 255), 5)
        cv2.line(img, (320, 150), (390, 200), (255, 255, 255), 5)
        
        # Legs
        cv2.line(img, (320, 300), (280, 400), (255, 255, 255), 5)
        cv2.line(img, (320, 300), (360, 400), (255, 255, 255), 5)
        
        # Add some background elements
        cv2.rectangle(img, (50, 350), (150, 450), (100, 100, 100), -1)
        cv2.rectangle(img, (500, 350), (600, 450), (100, 100, 100), -1)
        
        return img
    
    def start_demo_source(self):
        """Initialize demo source (image, video, or synthetic)."""
        if self.demo_source is None:
            # Create synthetic demo image
            print("Using synthetic demo image")
            self.is_image = True
            return True
        
        if not os.path.exists(self.demo_source):
            print(f"Demo source not found: {self.demo_source}")
            print("Falling back to synthetic demo image")
            self.is_image = True
            return True
        
        # Check if it's a video file
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv']
        if any(self.demo_source.lower().endswith(ext) for ext in video_extensions):
            self.cap = cv2.VideoCapture(self.demo_source)
            if self.cap.isOpened():
                self.is_video = True
                print(f"Using video file: {self.demo_source}")
                return True
            else:
                print(f"Could not open video file: {self.demo_source}")
                return False
        
        # Check if it's an image file
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        if any(self.demo_source.lower().endswith(ext) for ext in image_extensions):
            self.is_image = True
            print(f"Using image file: {self.demo_source}")
            return True
        
        print(f"Unsupported file format: {self.demo_source}")
        return False
    
    def get_next_frame(self):
        """Get the next frame from the demo source."""
        if self.is_image:
            if self.demo_source and os.path.exists(self.demo_source):
                frame = cv2.imread(self.demo_source)
                if frame is not None:
                    return True, frame
            # Use synthetic image
            return True, self.create_synthetic_demo_image()
        
        elif self.is_video and self.cap:
            ret, frame = self.cap.read()
            if not ret:
                # Loop the video
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()
            return ret, frame
        
        return False, None
    
    def run_demo(self):
        """Run the demo tracking loop."""
        try:
            if not self.start_demo_source():
                print("Failed to initialize demo source")
                return
            
            print("Starting MediaPipe Person Tracking Demo...")
            print("Press 'q' to quit, 's' to save current frame")
            print("Press 'p' to toggle pose detection, 'o' to toggle object detection")
            
            frame_count = 0
            start_time = time.time()
            show_pose = True
            show_objects = True
            
            while True:
                ret, frame = self.get_next_frame()
                if not ret:
                    print("Failed to get frame from demo source")
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
                
                # Add demo indicator
                demo_text = "DEMO MODE - No Camera Required"
                cv2.putText(processed_frame, demo_text, (frame.shape[1] - 300, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                
                # Display the frame
                cv2.imshow('MediaPipe Person Tracking - Demo Mode', processed_frame)
                
                # Handle key presses
                key = cv2.waitKey(30) & 0xFF  # Slower for demo
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    # Save current frame
                    filename = f"mediapipe_demo_frame_{int(time.time())}.jpg"
                    cv2.imwrite(filename, processed_frame)
                    print(f"Frame saved as {filename}")
                elif key == ord('p'):
                    show_pose = not show_pose
                    print(f"Pose detection: {'ON' if show_pose else 'OFF'}")
                elif key == ord('o'):
                    show_objects = not show_objects
                    print(f"Object detection: {'ON' if show_objects else 'OFF'}")
                
        except KeyboardInterrupt:
            print("\nDemo stopped by user")
        except Exception as e:
            print(f"Error during demo: {e}")
        finally:
            self.cleanup()


def main():
    """Main function to run the demo."""
    print("MediaPipe Person Tracking - Demo Mode")
    print("=" * 40)
    print("This demo works without a camera!")
    print("You can provide an image or video file as demo source.")
    print("=" * 40)
    
    import sys
    
    demo_source = None
    if len(sys.argv) > 1:
        demo_source = sys.argv[1]
        print(f"Using demo source: {demo_source}")
    else:
        print("Using synthetic demo image")
    
    try:
        # Create demo tracker instance
        tracker = DemoPersonTracker(demo_source=demo_source, confidence_threshold=0.5)
        
        # Start demo
        tracker.run_demo()
        
    except Exception as e:
        print(f"Demo error: {e}")
        print("Make sure you have:")
        print("1. MediaPipe properly installed")
        print("2. Required dependencies installed")


if __name__ == "__main__":
    main()
