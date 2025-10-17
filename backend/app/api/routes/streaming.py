import asyncio
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from app.api.deps import CurrentUserWS, get_db
from app.connection_manager import manager
from app.cv_model.frame_processor import get_frame_processor


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["video-streaming"])

@router.websocket("/video")
async def video_stream_endpoint(
    websocket: WebSocket,
    current_user: CurrentUserWS
) -> None:
    """
    WebSocket endpoint for authenticated video streaming with AI-powered person detection.
    
    This endpoint accepts WebSocket connections for real-time video streaming.
    Authentication is required via JWT token passed as a query parameter.
    The authenticated user's ID is used as the client identifier.
    
    Features:
        - Real-time person detection using YOLOv8
        - Automatic frame annotation with bounding boxes
        - Detection confidence scores
        - Frame statistics and monitoring
        - Automatic database persistence (every 5 seconds per tracked person)
        - QR code detection with exit functionality (when enabled)
    
    Clients can send video frames to be processed or broadcasted, and receive
    processed frames with person detection annotations from the server.
    
    Args:
        websocket: The WebSocket connection
        current_user: Authenticated user (injected via dependency)
        
    Protocol:
        - Binary messages: Video frames (JPEG, PNG, or raw frame data)
          - Frames are automatically processed with person detection
          - Processed frames with bounding boxes are sent back
        - Text messages: JSON control messages
          - {"action": "ping"} - Heartbeat message
          - {"action": "status"} - Request connection status
          - {"action": "configure", "confidence": 0.5, "enable_qr": false} - Configure detection
          - {"action": "broadcast", "data": "base64_frame"} - Broadcast frame to all clients
        
    Server Messages:
        - Binary: Processed video frames with person detection annotations
        - JSON: Detection results when persons are detected
          - {"type": "detection", "person_count": N, "avg_confidence": X, "detections": [...], "saved_to_db": N}
        - JSON: Exit QR code detection
          - {"type": "exit_detected", "message": "Exit QR code detected - connection will be closed"}
          
    Example usage from JavaScript client:
        ```javascript
        // First, get the access token from login
        const token = 'your-jwt-token';
        const ws = new WebSocket(`ws://localhost:8000/api/v1/ws/video?token=${token}`);
        
        ws.onopen = () => {
            console.log('Connected');
        };
        
        ws.onmessage = (event) => {
            if (event.data instanceof Blob) {
                // Handle video frame
                const img = document.getElementById('video-frame');
                img.src = URL.createObjectURL(event.data);
            } else {
                // Handle text message
                const data = JSON.parse(event.data);
                console.log('Status:', data);
            }
        };
        
        // Send video frame
        const sendFrame = (frameBlob) => {
            ws.send(frameBlob);
        };
        ```
        
    Authentication:
        The token must be a valid JWT access token obtained from the /login/access-token endpoint.
        If authentication fails, the connection will be closed with code 1008 (Policy Violation).
    """
    # User is already authenticated via dependency injection
    client_id = str(current_user.id)
    
    # Detection configuration (per-client settings)
    detection_config = {
        "confidence_threshold": 0.5,
        "enable_qr": True
    }
    
    # Get database session for detection persistence
    db_generator = get_db()
    session = next(db_generator)
    
    await manager.connect(websocket, client_id)
    
    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "client_id": client_id,
            "user_email": current_user.email,
            "message": f"WebSocket connection established for video streaming - User: {current_user.email}"
        })
        
        while True:
            # Receive data from client
            try:
                # Try to receive data with a timeout to allow for periodic checks
                data = await asyncio.wait_for(
                    websocket.receive(),
                    timeout=30.0  # 30 second timeout for heartbeat check
                )
                
                # Handle different types of messages
                if "bytes" in data:
                    # Received a video frame
                    frame_data = data["bytes"]
                    logger.debug(f"Received frame from {client_id}, size: {len(frame_data)} bytes")
                    
                    # Process frame with person detection
                    processor = get_frame_processor(
                        confidence_threshold=detection_config["confidence_threshold"],
                        enable_qr=detection_config["enable_qr"]
                    )
                    processed_frame, results = await processor.process_frame(frame_data, session=session)
                    
                    # Check for exit QR code
                    if results.get("has_exit_qr", False):
                        logger.info(f"Exit QR code detected for client {client_id} - terminating connection")
                        await websocket.send_json({
                            "type": "exit_detected",
                            "message": "Exit QR code detected - connection will be closed"
                        })
                        # Close the connection gracefully
                        await websocket.close(code=1000, reason="Exit QR code detected")
                        break
                    
                    if processed_frame:
                        # Send processed frame with detection annotations back to client
                        await websocket.send_bytes(processed_frame)
                        
                        # Send detection results as JSON (optional)
                        if results.get("person_count", 0) > 0:
                            await websocket.send_json({
                                "type": "detection",
                                "person_count": results["person_count"],
                                "avg_confidence": results.get("avg_confidence"),
                                "detections": results.get("detections", []),
                                "saved_to_db": results.get("saved_to_db", 0)
                            })
                    else:
                        # If processing failed, echo original frame
                        await websocket.send_bytes(frame_data)
                        logger.warning(f"Frame processing failed: {results.get('error', 'Unknown error')}")
                    
                    # Optionally broadcast processed frames to other clients
                    # await manager.broadcast_frame(processed_frame if processed_frame else frame_data)
                    
                elif "text" in data:
                    # Received a text message (control message)
                    import json
                    try:
                        message = json.loads(data["text"])
                        action = message.get("action")
                        
                        if action == "ping":
                            await websocket.send_json({"type": "pong", "timestamp": asyncio.get_event_loop().time()})
                        
                        elif action == "status":
                            await websocket.send_json({
                                "type": "status",
                                "client_id": client_id,
                                "active_connections": manager.get_active_connections_count()
                            })
                        
                        elif action == "configure":
                            # Update detection configuration
                            if "confidence" in message:
                                confidence = float(message["confidence"])
                                if 0.0 <= confidence <= 1.0:
                                    detection_config["confidence_threshold"] = confidence
                                else:
                                    await websocket.send_json({
                                        "type": "error",
                                        "message": "Confidence must be between 0.0 and 1.0"
                                    })
                                    continue
                            
                            if "enable_qr" in message:
                                detection_config["enable_qr"] = bool(message["enable_qr"])
                            
                            await websocket.send_json({
                                "type": "config_updated",
                                "confidence_threshold": detection_config["confidence_threshold"],
                                "enable_qr": detection_config["enable_qr"]
                            })
                        
                        elif action == "broadcast" and "data" in message:
                            # Broadcast a frame to all connected clients
                            import base64
                            frame_bytes = base64.b64decode(message["data"])
                            sent_count = await manager.broadcast_frame(frame_bytes)
                            await websocket.send_json({
                                "type": "broadcast_result",
                                "sent_to": sent_count
                            })
                        
                        else:
                            await websocket.send_json({
                                "type": "error",
                                "message": f"Unknown action: {action}"
                            })
                    
                    except json.JSONDecodeError:
                        await websocket.send_json({
                            "type": "error",
                            "message": "Invalid JSON format"
                        })
                
            except asyncio.TimeoutError:
                # Send heartbeat to keep connection alive
                try:
                    await websocket.send_json({"type": "heartbeat"})
                except Exception:
                    # If we can't send heartbeat, connection is likely dead
                    break
            
    except WebSocketDisconnect:
        logger.info(f"Client {client_id} disconnected normally")
    except Exception as e:
        logger.error(f"Error in WebSocket connection for {client_id}: {e}")
    finally:
        manager.disconnect(client_id)
        # Close database session
        try:
            session.close()
        except Exception as e:
            logger.error(f"Error closing database session for {client_id}: {e}")


@router.get("/video/connections/count")
async def get_connections_count() -> dict[str, int]:
    """
    Get the number of active WebSocket connections.
    
    Returns:
        Dictionary with the count of active connections
    """
    return {"active_connections": manager.get_active_connections_count()}

