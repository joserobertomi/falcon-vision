import cv2
import numpy as np
import logging
from typing import Tuple, List, Optional, Dict
from ultralytics import YOLO
from pyzbar import pyzbar
import uuid
import time
from sqlmodel import Session

from app.models import DetectionCreate
from app.crud import create_detection

logger = logging.getLogger(__name__)


class FrameProcessor:
    """
    Real-time frame processor for WebSocket video streaming.
    
    This class processes individual frames for person detection and QR code detection
    without requiring camera initialization. It's designed for WebSocket streaming
    where frames are received from clients.
    
    Features:
    - Person detection with tracking
    - QR code detection (optional)
    - Automatic database persistence every 5 seconds per tracked person
    
    Example usage in WebSocket endpoint:
        ```python
        from app.cv_model.frame_processor import get_frame_processor
        from app.api.deps import get_db
        
        processor = get_frame_processor()
        
        # When frame is received (with database persistence)
        session = next(get_db())
        processed_frame, results = await processor.process_frame(frame_bytes, session=session)
        await websocket.send_bytes(processed_frame)
        
        # Without database persistence
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
        
        # Person tracking
        self.active_persons: Dict[str, dict] = {}  # Track active persons by ID
        self.next_person_id = 1
        self.max_disappeared_frames = 5  # Remove person if not seen for 5 frames
        self.start_time = time.time()  # Track overall processing start time
        
        # Database persistence tracking
        self.last_db_save: Dict[str, float] = {}  # Track last DB save time for each person
        self.db_save_interval = 5.0  # Save to DB every 5 seconds
        
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

    def calculate_iou(self, bbox1: Tuple[int, int, int, int], bbox2: Tuple[int, int, int, int]) -> float:
        """
        Calculate Intersection over Union (IoU) between two bounding boxes.
        
        Args:
            bbox1: First bounding box (x1, y1, x2, y2)
            bbox2: Second bounding box (x1, y1, x2, y2)
            
        Returns:
            IoU value between 0 and 1
        """
        x1_1, y1_1, x2_1, y2_1 = bbox1
        x1_2, y1_2, x2_2, y2_2 = bbox2
        
        # Calculate intersection area
        x1_i = max(x1_1, x1_2)
        y1_i = max(y1_1, y1_2)
        x2_i = min(x2_1, x2_2)
        y2_i = min(y2_1, y2_2)
        
        if x2_i <= x1_i or y2_i <= y1_i:
            return 0.0
        
        intersection = (x2_i - x1_i) * (y2_i - y1_i)
        
        # Calculate union area
        area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
        area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0

    def match_persons(self, current_detections: List[Tuple[int, int, int, int]]) -> List[Tuple[str, Tuple[int, int, int, int]]]:
        """
        Match current detections with existing tracked persons.
        
        Args:
            current_detections: List of current bounding boxes
            
        Returns:
            List of (person_id, bbox) tuples for matched persons
        """
        matched_persons = []
        used_detections = set()
        
        # Try to match each existing person with current detections
        for person_id, person_data in self.active_persons.items():
            best_iou = 0.0
            best_detection_idx = -1
            
            for i, detection_bbox in enumerate(current_detections):
                if i in used_detections:
                    continue
                    
                iou = self.calculate_iou(person_data['bbox'], detection_bbox)
                if iou > best_iou and iou > 0.3:  # Minimum IoU threshold
                    best_iou = iou
                    best_detection_idx = i
            
            if best_detection_idx != -1:
                # Match found
                matched_bbox = current_detections[best_detection_idx]
                matched_persons.append((person_id, matched_bbox))
                used_detections.add(best_detection_idx)
                
                # Update person data
                self.active_persons[person_id]['bbox'] = matched_bbox
                self.active_persons[person_id]['last_seen'] = self.frames_processed
                self.active_persons[person_id]['last_detection_time'] = time.time()
        
        # Create new persons for unmatched detections
        for i, detection_bbox in enumerate(current_detections):
            if i not in used_detections:
                new_person_id = f"person_{self.next_person_id}"
                self.next_person_id += 1
                
                current_time = time.time()
                self.active_persons[new_person_id] = {
                    'bbox': detection_bbox,
                    'first_detected': self.frames_processed,
                    'last_seen': self.frames_processed,
                    'first_detection_time': current_time,
                    'last_detection_time': current_time
                }
                
                matched_persons.append((new_person_id, detection_bbox))
        
        # Remove persons that haven't been seen for too long
        persons_to_remove = []
        for person_id, person_data in self.active_persons.items():
            if self.frames_processed - person_data.get('last_seen', 0) > self.max_disappeared_frames:
                persons_to_remove.append(person_id)
        
        for person_id in persons_to_remove:
            del self.active_persons[person_id]
            # Also clean up DB save tracking
            if person_id in self.last_db_save:
                del self.last_db_save[person_id]
        
        return matched_persons


    def detect_persons(self, frame: np.ndarray) -> Tuple[np.ndarray, int, List[dict]]:
        """
        Detect persons in the frame using YOLOv8 with tracking.
        
        Args:
            frame: Input frame as numpy array
            
        Returns:
            tuple: (frame_with_detections, person_count, detections_info)
        """
        # Run YOLOv8 inference
        results = self.model(frame, verbose=False)
        
        # Collect all person detections
        current_detections = []
        detection_confidences = []
        
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
                    bbox = (x1, y1, x2, y2)
                    current_detections.append(bbox)
                    detection_confidences.append(confidence)
        
        # Match detections with existing persons or create new ones
        matched_persons = self.match_persons(current_detections)
        
        # Create annotated frame and results
        annotated_frame = frame.copy()
        detections_info = []
        
        for person_id, bbox in matched_persons:
            x1, y1, x2, y2 = bbox
            
            # Find confidence for this detection
            confidence = 0.0
            for i, detection_bbox in enumerate(current_detections):
                if detection_bbox == bbox:
                    confidence = detection_confidences[i]
                    break
            
            # Calculate elapsed time since first detection
            person_data = self.active_persons[person_id]
            elapsed_time = person_data['last_detection_time'] - person_data['first_detection_time']
            
            # Log person detection with ID, bbox, and elapsed time
            logger.info(f"Person detected: {{'id': '{person_id}', 'bbox': {bbox}, 'elapsed_time': {elapsed_time:.2f}}}")
            
            # Draw bounding box
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw label with ID and confidence
            label = f'{person_id} ({confidence:.2f})'
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            
            # Draw label background
            cv2.rectangle(annotated_frame, 
                        (x1, y1 - label_size[1] - 10), 
                        (x1 + label_size[0], y1), 
                        (0, 255, 0), -1)
            
            # Draw label text
            cv2.putText(annotated_frame, label, (x1, y1 - 5), 
                      cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
            
            # Calculate elapsed time for this person
            person_data = self.active_persons[person_id]
            elapsed_time = person_data['last_detection_time'] - person_data['first_detection_time']
            
            detections_info.append({
                'id': person_id,
                'bbox': bbox,
                'confidence': confidence,
                'elapsed_time': round(elapsed_time, 2),
                'first_detection_time': person_data['first_detection_time'],
                'last_detection_time': person_data['last_detection_time']
            })
        
        return annotated_frame, len(matched_persons), detections_info
    
    def save_detections_to_db(self, detections_info: List[dict], session: Session) -> int:
        """
        Save detections to database if enough time has elapsed since last save.
        
        Only saves detections where elapsed_time > 0 to ensure we're tracking persons
        over time, not just instantaneous detections.
        
        Args:
            detections_info: List of detection information dictionaries
            session: Database session for persistence
            
        Returns:
            Number of detections saved to database
        """
        saved_count = 0
        current_time = time.time()
        
        for detection in detections_info:
            person_id = detection['id']
            elapsed_time = detection['elapsed_time']
            
            # Validate: only save detections with elapsed_time > 0
            if elapsed_time <= 0:
                logger.debug(f"Skipping {person_id}: elapsed_time is {elapsed_time:.2f}s (must be > 0)")
                continue
            
            last_save_time = self.last_db_save.get(person_id, 0)
            
            # Check if 5 seconds have elapsed since last save
            if current_time - last_save_time >= self.db_save_interval:
                try:
                    # Extract bbox coordinates
                    x1, y1, x2, y2 = detection['bbox']
                    
                    # Create detection record
                    detection_create = DetectionCreate(
                        person_id=person_id,
                        bbox_x1=x1,
                        bbox_y1=y1,
                        bbox_x2=x2,
                        bbox_y2=y2,
                        confidence=detection['confidence'],
                        elapsed_time=elapsed_time,
                        first_detection_time=detection['first_detection_time'],
                        last_detection_time=detection['last_detection_time']
                    )
                    
                    # Save to database
                    create_detection(session=session, detection_in=detection_create)
                    
                    # Update last save time
                    self.last_db_save[person_id] = current_time
                    saved_count += 1
                    
                    logger.info(f"Saved detection for {person_id} to database (elapsed: {elapsed_time:.2f}s)")
                    
                except Exception as e:
                    logger.error(f"Failed to save detection for {person_id} to database: {e}")
        
        return saved_count
    
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
        # Dynamically fit background rectangle to content
        y_start = 10
        x_start = 10
        x_pad = 14
        y_pad = 8
        row_height = 18
        num_lines = 1 + (1 if self.enable_qr else 0) + (1 if avg_confidence is not None and person_count > 0 else 0)
        # Estimate width (max of all text lines)
        text_labels = [f"Persons: {person_count}"]
        if self.enable_qr:
            text_labels.append(f"QR codes: {qr_count}")
        if avg_confidence is not None and person_count > 0:
            text_labels.append(f"Avg Conf: {avg_confidence:.2f}")
        text_widths = [cv2.getTextSize(l, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)[0][0] for l in text_labels]
        box_width = max(text_widths)+x_pad*2
        box_height = num_lines * row_height + y_pad*2

        cv2.rectangle(
            frame, 
            (x_start, y_start), 
            (x_start + box_width, y_start + box_height),
            (0, 0, 0), -1
        )
        cv2.rectangle(
            frame,
            (x_start, y_start),
            (x_start + box_width, y_start + box_height),
            (255, 255, 255), 2
        )
        
        # Add text information (smaller font and tighter layout)
        y_pos = 25
        font_scale = 0.45
        line_spacing = 18
        thickness = 1

        cv2.putText(frame, f"Persons: {person_count}", (15, y_pos),
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 255, 0), thickness)

        if self.enable_qr:
            y_pos += line_spacing
            cv2.putText(frame, f"QR codes: {qr_count}", (15, y_pos),
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 0, 0), thickness)

        if avg_confidence is not None and person_count > 0:
            y_pos += line_spacing
            cv2.putText(frame, f"Avg Conf: {avg_confidence:.2f}", (15, y_pos),
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 255, 255), thickness)
        
    
    async def process_frame(self, frame_bytes: bytes, session: Optional[Session] = None) -> Tuple[Optional[bytes], dict]:
        """
        Process a single frame with person detection.
        
        Args:
            frame_bytes: Input frame as bytes (JPEG, PNG, etc.)
            session: Optional database session for persisting detections
            
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
            
            # Save detections to database if session is provided
            saved_count = 0
            if session is not None and detections_info:
                saved_count = self.save_detections_to_db(detections_info, session)
            
            # Prepare results
            results = {
                "person_count": person_count,
                "detections": detections_info,
                "avg_confidence": avg_confidence,
                "qr_codes": qr_data_list if self.enable_qr else [],
                "frames_processed": self.frames_processed,
                "saved_to_db": saved_count
            }
            
            # Log summary of detected persons with their IDs, bbox positions, and elapsed times
            if detections_info:
                detection_summary = []
                for detection in detections_info:
                    person_id = detection['id']
                    person_data = self.active_persons[person_id]
                    elapsed_time = person_data['last_detection_time'] - person_data['first_detection_time']
                    
                    detection_summary.append({
                        'id': person_id,
                        'bbox': detection['bbox'],
                        'elapsed_time': round(elapsed_time, 2),
                        'confidence': detection['confidence']
                    })
                logger.info(f"Frame {self.frames_processed} summary: {detection_summary}")
            
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

