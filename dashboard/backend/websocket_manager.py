"""
WebSocket connection manager for real-time updates
"""
from typing import List, Set
from fastapi import WebSocket
import json
from .models import WebSocketMessage


class WebSocketManager:
    """Manages WebSocket connections and broadcasting"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept and store a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"✅ WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"❌ WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket"""
        await websocket.send_text(message)
    
    async def broadcast(self, message: WebSocketMessage):
        """Broadcast a message to all connected clients"""
        if not self.active_connections:
            return
            
        message_json = json.dumps(message.dict(), default=str)
        
        # Send to all connected clients
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message_json)
            except Exception:
                # Connection is closed, mark for removal
                disconnected.append(connection)
        
        # Remove disconnected clients
        for conn in disconnected:
            self.disconnect(conn)
    
    async def broadcast_to_project(self, project_id: str, message: WebSocketMessage):
        """Broadcast a message related to a specific project"""
        message.project_id = project_id
        await self.broadcast(message)