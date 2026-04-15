# backend/src/todo_backend/infrastructure/notification/websocket_manager.py
import logging
from typing import Any, Dict, List

from fastapi import WebSocket

from todo_backend.domain.repositories_interface.notification_repository import \
    NotificationRepository

logger = logging.getLogger(__name__)

class WebSocketManager(NotificationRepository):
    """
    Quản lý các kết nối WebSocket đang hoạt động.
    Lớp này thực thi NotificationRepository.
    """
    def __init__(self):
        # Lưu kết nối: {user_id: [list_of_websocket_connections]}
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        """Chấp nhận và lưu kết nối mới."""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        logger.info(f"WebSocket connected: User {user_id} (Total {len(self.active_connections[user_id])} connections)")

    def disconnect(self, user_id: int, websocket: WebSocket):
        """Xóa kết nối khi người dùng ngắt kết nối."""
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
            logger.info(f"WebSocket disconnected: User {user_id}")
            
    async def send_to_user(self, user_id: int, message: str):
        """
        Gửi tin nhắn đến tất cả các kết nối (tab trình duyệt)
        của một user_id cụ thể.
        """
        payload = {
            "event": "notification.message",
            "message": message,
        }
        await self.send_json_to_user(user_id, payload)

    async def send_json_to_user(self, user_id: int, payload: Dict[str, Any]):
        """
        Gửi payload JSON đến tất cả các kết nối của user.
        """
        if user_id in self.active_connections:
            connections = list(self.active_connections[user_id])
            logger.info(f"Sending WS payload to User {user_id} ({len(connections)} connections)")
            for connection in connections:
                try:
                    await connection.send_json(payload)
                except Exception as e:
                    logger.error(f"Failed to send message to User {user_id}: {e}")
                    self.disconnect(user_id, connection)

# --- QUAN TRỌNG: Tạo một Singleton Instance ---
# Chúng ta cần MỘT trung tâm quản lý duy nhất
# mà cả API (endpoint) và Scheduler (background job) đều có thể truy cập.
websocket_manager = WebSocketManager()