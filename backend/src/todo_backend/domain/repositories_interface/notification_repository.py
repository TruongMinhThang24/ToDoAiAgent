# backend/src/todo_backend/domain/repositories_interface/notification_repository.py
from abc import ABC, abstractmethod

class NotificationRepository(ABC):
    """
    Interface cho dịch vụ gửi thông báo.
    """
    @abstractmethod
    async def send_to_user(self, user_id: int, message: str):
        """
        Gửi một tin nhắn (dạng string) đến một user_id cụ thể.
        """
        pass