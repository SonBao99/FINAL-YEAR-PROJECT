from fastapi import WebSocket
from typing import Dict, List
import json

class ConnectionManager:
    def __init__(self):
        # Dictionary to store active connections by session_id
        self.active_connections: Dict[int, List[WebSocket]] = {}
        self.video_stream_connections: List[WebSocket] = []  # For video streaming viewers
        self.video_stream_source = None  # Kiosk connection that sends frames

    async def connect(self, websocket: WebSocket, session_id: int):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)

    def disconnect(self, websocket: WebSocket, session_id: int):
        if session_id in self.active_connections:
            if websocket in self.active_connections[session_id]:
                self.active_connections[session_id].remove(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
        # Also remove from video stream connections
        if websocket in self.video_stream_connections:
            self.video_stream_connections.remove(websocket)
        if self.video_stream_source == websocket:
            self.video_stream_source = None

    async def broadcast_to_session(self, session_id: int, message: dict):
        if session_id in self.active_connections:
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    # Remove broken connections
                    if connection in self.active_connections[session_id]:
                        self.active_connections[session_id].remove(connection)

    async def connect_video_stream_source(self, websocket: WebSocket):
        """Connect kiosk as video stream source"""
        await websocket.accept()
        self.video_stream_source = websocket

    async def disconnect_video_stream_source(self, websocket: WebSocket):
        """Disconnect kiosk video stream source"""
        if self.video_stream_source == websocket:
            self.video_stream_source = None

    async def connect_video_viewer(self, websocket: WebSocket):
        """Connect web dashboard as video stream viewer"""
        await websocket.accept()
        self.video_stream_connections.append(websocket)

    async def disconnect_video_viewer(self, websocket: WebSocket):
        """Disconnect web dashboard video viewer"""
        if websocket in self.video_stream_connections:
            self.video_stream_connections.remove(websocket)

    async def broadcast_video_frame(self, frame_base64: str):
        """Broadcast video frame from kiosk to all connected web viewers"""
        if self.video_stream_connections:
            disconnected = []
            message = json.dumps({
                "type": "video_frame",
                "frame": frame_base64
            })
            for connection in self.video_stream_connections:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    disconnected.append(connection)
            # Remove disconnected clients
            for conn in disconnected:
                if conn in self.video_stream_connections:
                    self.video_stream_connections.remove(conn)

    async def broadcast_stats_update(self, stats: dict):
        """Broadcast stats update from kiosk to all connected web viewers"""
        if self.video_stream_connections:
            disconnected = []
            message = json.dumps({
                "type": "stats_update",
                "stats": stats
            })
            for connection in self.video_stream_connections:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    disconnected.append(connection)
            # Remove disconnected clients
            for conn in disconnected:
                if conn in self.video_stream_connections:
                    self.video_stream_connections.remove(conn)
