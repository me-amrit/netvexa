from typing import Dict, List
from fastapi import WebSocket
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # Store active connections by agent_id
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, agent_id: str):
        """Accept new WebSocket connection"""
        await websocket.accept()
        
        if agent_id not in self.active_connections:
            self.active_connections[agent_id] = []
        
        self.active_connections[agent_id].append(websocket)
        logger.info(f"New WebSocket connection for agent {agent_id}")
    
    def disconnect(self, websocket: WebSocket, agent_id: str):
        """Remove WebSocket connection"""
        if agent_id in self.active_connections:
            if websocket in self.active_connections[agent_id]:
                self.active_connections[agent_id].remove(websocket)
                logger.info(f"WebSocket disconnected for agent {agent_id}")
            
            # Clean up empty lists
            if not self.active_connections[agent_id]:
                del self.active_connections[agent_id]
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific WebSocket"""
        await websocket.send_text(message)
    
    async def broadcast(self, message: str, agent_id: str):
        """Broadcast message to all connections for an agent"""
        if agent_id in self.active_connections:
            for connection in self.active_connections[agent_id]:
                await connection.send_text(message)