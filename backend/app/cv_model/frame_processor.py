import cv2
import numpy as np
import logging
from typing import Tuple, List, Optional
from ultralytics import YOLO
from pyzbar import pyzbar

logger = logging.getLogger(__name__)


class FrameProcessor:
    """
    Real-time frame processor for WebSocket video streaming.
    
    This class processes individual frames for person detection and QR code detection
    without requiring camera initialization. It's designed for WebSocket streaming
    where frames are received from clients.
    
    Example usage in WebSocket endpoint:
        ```python
        from app.cv_model.frame_processor import get_frame_processor
        
        processor = get_frame_processor()
        
        # When frame is received
        processed_frame, results = await processor.process_frame(frame_bytes)
        await websocket.send_bytes(processed_frame)
        ```
    """
    
    def __init__(self, confidence_threshold: float = 0.5, enable_qr: bool = False):
        """
        Initialize the frame processor.
        
        Args:
            confidence_threshold: Minimum confidence for person detection (0.0-1.0)
            enable_qr: Whether to enable QR code detection
        """
        self.confidence_threshold = confidence_threshold
        self.enable_qr = enable_qr
        
        # Initialize YOLOv8 model
        logger.info("Loading YOLOv8 model for frame processing...")
        self.model = YOLO('yolov8n.pt')  # nano version for speed
        
        # COCO dataset class for person is 0
        self.person_class_id = 0
        
        # Statistics
        self.frames_processed = 0
        
        logger.info("FrameProcessor initialized successfully!")
    
    def decode_frame(self, frame_bytes: bytes) -> Optional[np.ndarray]:
        """
        Decode frame bytes to numpy array.
        
        Args:
            frame_bytes: Frame data as bytes (JPEG, PNG, etc.)
            
        Returns:
            Decoded frame as numpy array, or None if decoding fails
        """
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(frame_bytes, np.uint8)
            # Decode image
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return frame
        except Exception as e:
            logger.error(f"Failed to decode frame: {e}")
            return None
    
    def encode_frame(self, frame: np.ndarray, quality: int = 80) -> Optional[bytes]:
        """
        Encode frame to JPEG bytes.
        
        Args:
            frame: Frame as numpy array
            quality: JPEG quality (0-100)
            
        Returns:
            Encoded frame as bytes, or None if encoding fails
        """
        try:
            success, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
            if not success:
                logger.error("Failed to encode frame")
                return None
            return buffer.tobytes()
        except Exception as e:
            logger.error(f"Failed to encode frame: {e}")
            return None
    
    def detect_qr_codes(self, frame: np.ndarray) -> Tuple[np.ndarray, List[str]]:
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

    def detect_persons(self, frame: np.ndarray) -> Tuple[np.ndarray, int, List[dict]]:
        """
        Detect persons in the frame using YOLOv8.
        
        Args:
            frame: Input frame as numpy array
            
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
    
    def draw_info_overlay(self, frame: np.ndarray, person_count: int, 
                          avg_confidence: Optional[float] = None, qr_count: int = 0):
        """
        Draw information overlay on the frame.
        
        Args:
            frame: Frame to draw on (modified in place)
            person_count: Number of persons detected
            avg_confidence: Average confidence of detections
            qr_count: Number of QR codes detected
        """
        # Background rectangle for text
        overlay_height = 120 if not self.enable_qr else 140
        cv2.rectangle(frame, (10, 10), (300, overlay_height), (0, 0, 0), -1)
        cv2.rectangle(frame, (10, 10), (300, overlay_height), (255, 255, 255), 2)
        
        # Add text information
        y_pos = 35
        cv2.putText(frame, f"Persons detected: {person_count}", (20, y_pos), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        if self.enable_qr:
            y_pos += 30
            cv2.putText(frame, f"QR codes: {qr_count}", (20, y_pos), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        
        if avg_confidence is not None and person_count > 0:
            y_pos += 30
            cv2.putText(frame, f"Avg Confidence: {avg_confidence:.2f}", (20, y_pos), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        y_pos += 30
        cv2.putText(frame, f"Frames: {self.frames_processed}", (20, y_pos), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    async def process_frame(self, frame_bytes: bytes) -> Tuple[Optional[bytes], dict]:
        """
        Process a single frame with person detection.
        
        Args:
            frame_bytes: Input frame as bytes (JPEG, PNG, etc.)
            
        Returns:
            tuple: (processed_frame_bytes, results_dict)
                - processed_frame_bytes: Annotated frame as JPEG bytes
                - results_dict: Dictionary with detection results
        """
        try:
            # Decode frame
            frame = self.decode_frame(frame_bytes)
            if frame is None:
                return None, {"error": "Failed to decode frame"}
            
            # Process QR codes if enabled
            qr_data_list = []
            if self.enable_qr:
                frame, qr_data_list = self.detect_qr_codes(frame)
            
            # Detect persons
            annotated_frame, person_count, detections_info = self.detect_persons(frame)
            
            # Calculate average confidence
            avg_confidence = None
            if detections_info:
                avg_confidence = sum(d['confidence'] for d in detections_info) / len(detections_info)
            
            # Draw information overlay
            self.draw_info_overlay(annotated_frame, person_count, avg_confidence, len(qr_data_list))
            
            # Encode frame
            processed_bytes = self.encode_frame(annotated_frame)
            if processed_bytes is None:
                return None, {"error": "Failed to encode frame"}
            
            # Update statistics
            self.frames_processed += 1
            
            # Prepare results
            results = {
                "person_count": person_count,
                "detections": detections_info,
                "avg_confidence": avg_confidence,
                "qr_codes": qr_data_list if self.enable_qr else [],
                "frames_processed": self.frames_processed
            }
            
            logger.debug(f"Frame processed: {person_count} persons detected")
            
            return processed_bytes, results
            
        except Exception as e:
            logger.error(f"Error processing frame: {e}")
            return None, {"error": str(e)}


# Global frame processor instance (lazy initialization)
_frame_processor: Optional[FrameProcessor] = None


def get_frame_processor(confidence_threshold: float = 0.5, enable_qr: bool = False) -> FrameProcessor:
    """
    Get or create the global frame processor instance.
    
    Args:
        confidence_threshold: Minimum confidence for person detection
        enable_qr: Whether to enable QR code detection
        
    Returns:
        FrameProcessor instance
    """
    global _frame_processor
    if _frame_processor is None:
        _frame_processor = FrameProcessor(confidence_threshold, enable_qr)
    return _frame_processor

