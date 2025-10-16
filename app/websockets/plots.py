from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Set
import sys
sys.path.append("../../")
from auth import verify_websocket_token

router = APIRouter()

class ConnectionManager:
    """Manage active WebSocket connections"""
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        """Add new WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        self.active_connections.discard(websocket)

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                disconnected.add(connection)
        for conn in disconnected:
            self.disconnect(conn)

manager = ConnectionManager()

@router.websocket("/plots")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    """WebSocket endpoint for plot notifications"""
    await verify_websocket_token(websocket, token)
    await manager.connect(websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
