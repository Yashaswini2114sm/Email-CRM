from fastapi import WebSocket, WebSocketDisconnect

from src.core.logger import setup_logger

logger = setup_logger(__name__)


class ConnectionManager:
    """
    Manages active WebSocket connections for real-time notifications.
    Keeps a mapping of user_id -> websocket so we can push updates
    to specific users or broadcast to everyone.
    """

    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"WebSocket connected: user {user_id}")

    def disconnect(self, user_id: str):
        """Remove a disconnected user."""
        self.active_connections.pop(user_id, None)
        logger.info(f"WebSocket disconnected: user {user_id}")

    async def send_to_user(self, user_id: str, message: dict):
        """Send a JSON message to a specific connected user."""
        ws = self.active_connections.get(user_id)
        if ws:
            try:
                await ws.send_json(message)
            except Exception:
                self.disconnect(user_id)

    async def broadcast(self, message: dict):
        """Send a JSON message to all connected users."""
        disconnected = []
        for user_id, ws in self.active_connections.items():
            try:
                await ws.send_json(message)
            except Exception:
                disconnected.append(user_id)

        for user_id in disconnected:
            self.disconnect(user_id)


# Single instance shared across the application
manager = ConnectionManager()
