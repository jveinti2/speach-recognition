from fastapi import WebSocket
from typing import Dict


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str = "default"):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        print(f"WebSocket conectado: {client_id}")

    def disconnect(self, client_id: str = "default"):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            print(f"WebSocket desconectado: {client_id}")

    async def send_json(self, message: dict, client_id: str = "default"):
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            await websocket.send_json(message)

    async def broadcast(self, message: dict):
        for client_id, websocket in self.active_connections.items():
            await websocket.send_json(message)
