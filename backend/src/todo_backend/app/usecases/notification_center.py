from __future__ import annotations

from datetime import datetime
from typing import Optional

from todo_backend.domain.entities.models import Notification, Todo
from todo_backend.domain.repositories_interface.notification_center_repository import NotificationCenterRepository
from todo_backend.infrastructure.notification.websocket_manager import websocket_manager


class NotificationCenterUseCases:
    def __init__(self, repository: NotificationCenterRepository):
        self.repository = repository

    @staticmethod
    def _to_payload(notification: Notification) -> dict:
        return {
            "id": notification.id,
            "user_id": notification.user_id,
            "type": notification.type,
            "title": notification.title,
            "message": notification.message,
            "metadata": notification.metadata_json or {},
            "is_read": notification.is_read,
            "created_at": notification.created_at.isoformat() if notification.created_at else None,
            "read_at": notification.read_at.isoformat() if notification.read_at else None,
        }

    def list_notifications(
        self,
        *,
        user_id: int,
        is_read: Optional[bool],
        limit: int,
        offset: int,
    ) -> tuple[list[dict], int]:
        items, total = self.repository.list_notifications(
            user_id=user_id,
            is_read=is_read,
            limit=limit,
            offset=offset,
        )
        return [self._to_payload(item) for item in items], total

    def unread_count(self, *, user_id: int) -> int:
        return self.repository.count_unread(user_id=user_id)

    def mark_read(self, *, user_id: int, notification_id: int) -> Optional[dict]:
        item = self.repository.get_notification_for_owner(notification_id=notification_id, user_id=user_id)
        if not item:
            return None
        updated = self.repository.mark_as_read(notification=item)
        return self._to_payload(updated)

    def mark_all_read(self, *, user_id: int) -> int:
        return self.repository.mark_all_as_read(user_id=user_id)

    async def create_due_soon_notification(self, todo: Todo) -> Optional[dict]:
        if not todo.due_date:
            return None

        duplicate = self.repository.find_recent_due_soon_duplicate(
            user_id=todo.owner_id,
            todo_id=todo.id,
            due_date=todo.due_date,
            lookback_minutes=10,
        )
        if duplicate:
            return None

        title = "Todo sắp đến hạn"
        message = f"Công việc '{todo.title}' sẽ đến hạn lúc {todo.due_date.strftime('%H:%M %d/%m/%Y')}"
        created = self.repository.create_notification(
            user_id=todo.owner_id,
            notification_type="todo_due_soon",
            title=title,
            message=message,
            metadata={
                "todo_id": todo.id,
                "due_date": todo.due_date.isoformat(),
            },
        )

        unread_count = self.repository.count_unread(user_id=todo.owner_id)
        payload = {
            "event": "notification.created",
            "notification": self._to_payload(created),
            "unread_count": unread_count,
            "created_at": datetime.utcnow().isoformat(),
        }
        await websocket_manager.send_json_to_user(todo.owner_id, payload)
        return payload
