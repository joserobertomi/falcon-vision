from fastapi import WebSocket
from fastapi.websockets import WebSocketState

import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    """
    Manages WebSocket connections for video streaming.
    
    This manager handles multiple client connections and allows broadcasting
    video frames to all connected clients or sending frames to specific clients.
    """

    def __init__(self) -> None:
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str) -> None:
        """Accept a new WebSocket connection and store it."""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, client_id: str) -> None:
        """Remove a WebSocket connection from active connections."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Client {client_id} disconnected. Total connections: {len(self.active_connections)}")

    async def send_frame(self, client_id: str, frame: bytes) -> bool:
        """
        Send a video frame to a specific client.
        
        Args:
            client_id: The unique identifier for the client
            frame: The video frame data as bytes
            
        Returns:
            bool: True if frame was sent successfully, False otherwise
        """
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            try:
                if websocket.client_state == WebSocketState.CONNECTED:
                    await websocket.send_bytes(frame)
                    return True
            except Exception as e:
                logger.error(f"Error sending frame to {client_id}: {e}")
                self.disconnect(client_id)
        return False

    async def broadcast_frame(self, frame: bytes) -> int:
        """
        Broadcast a video frame to all connected clients.
        
        Args:
            frame: The video frame data as bytes
            
        Returns:
            int: Number of clients that successfully received the frame
        """
        disconnected_clients = []
        sent_count = 0

        for client_id, websocket in self.active_connections.items():
            try:
                if websocket.client_state == WebSocketState.CONNECTED:
                    await websocket.send_bytes(frame)
                    sent_count += 1
                else:
                    disconnected_clients.append(client_id)
            except Exception as e:
                logger.error(f"Error broadcasting to {client_id}: {e}")
                disconnected_clients.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)

        return sent_count

    async def send_text(self, client_id: str, message: str) -> bool:
        """
        Send a text message to a specific client.
        
        Args:
            client_id: The unique identifier for the client
            message: The text message to send
            
        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            try:
                if websocket.client_state == WebSocketState.CONNECTED:
                    await websocket.send_text(message)
                    return True
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {e}")
                self.disconnect(client_id)
        return False

    def get_active_connections_count(self) -> int:
        """Return the number of active connections."""
        return len(self.active_connections)


# Global connection manager instance
manager = ConnectionManager()