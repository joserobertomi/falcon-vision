import jwt
import logging
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session

from fastapi import WebSocket
from fastapi.websockets import WebSocketState

from app.core import security
from app.core.config import settings
from app.core.db import engine
from app.models import TokenPayload, User

logger = logging.getLogger(__name__)  ## IMPROVE LOGGING

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
    
    async def get_current_user_ws(self, token: str) -> User:
        """
        Authenticate WebSocket connection using JWT token.
        
        Args:
            token: JWT access token
            
        Returns:
            Authenticated user
            
        Raises:
            InvalidTokenError: If token is invalid or expired
            ValueError: If user not found or inactive
        """
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
            )
            token_data = TokenPayload(**payload)
        except (InvalidTokenError, ValidationError) as e:
            logger.error(f"Token validation failed: {e}")
            raise InvalidTokenError("Could not validate credentials")
        
        with Session(engine) as session:
            user = session.get(User, token_data.sub)
            if not user:
                raise ValueError("User not found")
            if not user.is_active:
                raise ValueError("Inactive user")
            return user


# Global connection manager instance
manager = ConnectionManager()