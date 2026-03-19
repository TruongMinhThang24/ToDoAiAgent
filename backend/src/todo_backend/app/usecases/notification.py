# ...existing code...
import logging 
from todo_backend.domain.entities.models import Todo
from todo_backend.domain.repositories_interface.notification_repository import \
    NotificationRepository
from fastapi import (APIRouter, Depends, WebSocket, WebSocketDisconnect,
                     status, HTTPException)
from sqlalchemy.orm import Session
# ...existing code...
# removed incorrect import that caused ImportError / circular import
# from .auth import validate_token_and_get_user, get_db
logger = logging.getLogger(__name__)
# ...existing code...
class NotificationUseCases:
    def __init__(self, notification_repo: NotificationRepository):
        self.notification_repo = notification_repo

    async def send_reminder_notification(self, todo: Todo):
        """
        Tạo và gửi tin nhắn nhắc nhở cho một todo.
        """
        if not todo or not todo.owner_id:
            logger.warning("Attempted to send reminder for invalid todo")
            return

        # Định dạng tin nhắn (sau này có thể dùng JSON)
        message = f"NHẮC NHỞ: Công việc '{todo.title}' của bạn sắp hết hạn lúc {todo.due_date.strftime('%H:%M %d/%m/%Y')}!"
        
        try:
            await self.notification_repo.send_to_user(todo.owner_id, message)
        except Exception as e:
            logger.exception("Failed to send reminder notification: %s", e)
# ...existing code...