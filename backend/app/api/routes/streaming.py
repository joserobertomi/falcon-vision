import asyncio
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from jwt.exceptions import InvalidTokenError

from app.connection_manager import manager


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["video-streaming"])



@router.websocket("/video")
async def video_stream_endpoint(
    websocket: WebSocket,
    token: str = Query(..., description="JWT access token for authentication")
) -> None:
    """
    WebSocket endpoint for authenticated video streaming.
    
    This endpoint accepts WebSocket connections for real-time video streaming.
    Authentication is required via JWT token passed as a query parameter.
    The authenticated user's ID is used as the client identifier.
    
    Clients can send video frames to be processed or broadcasted, and receive
    video frames from the server.
    
    Args:
        websocket: The WebSocket connection
        token: JWT access token for authentication (query parameter)
        
    Protocol:
        - Binary messages: Video frames (JPEG, PNG, or raw frame data)
        - Text messages: JSON control messages
          - {"action": "ping"} - Heartbeat message
          - {"action": "status"} - Request connection status
          - {"action": "broadcast", "data": "base64_frame"} - Broadcast frame to all clients
          
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
    # Authenticate user before accepting connection
    try:
        current_user = await manager.get_current_user_ws(token)
        client_id = str(current_user.id)
    except (InvalidTokenError, ValueError) as e:
        logger.warning(f"WebSocket authentication failed: {e}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Authentication failed")
        return
    
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
                    
                    # Here you can process the frame (e.g., run AI inference, object detection, etc.)
                    # For now, we'll just echo it back as an example
                    await websocket.send_bytes(frame_data)
                    
                    # Optionally broadcast to other clients
                    # await manager.broadcast_frame(frame_data)
                    
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


@router.get("/video/connections/count")
async def get_connections_count() -> dict[str, int]:
    """
    Get the number of active WebSocket connections.
    
    Returns:
        Dictionary with the count of active connections
    """
    return {"active_connections": manager.get_active_connections_count()}

