from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from todo_backend.domain.entities.models import Notification, Todo


class NotificationCenterRepository(ABC):
    """Repository contract cho Notification Center persistent data."""

    @abstractmethod
    def list_notifications(
        self,
        *,
        user_id: int,
        is_read: Optional[bool],
        limit: int,
        offset: int,
    ) -> tuple[list[Notification], int]:
        """Trả về danh sách notifications + tổng số bản ghi theo filter."""

    @abstractmethod
    def count_unread(self, *, user_id: int) -> int:
        """Đếm số notifications chưa đọc của user."""

    @abstractmethod
    def create_notification(
        self,
        *,
        user_id: int,
        notification_type: str,
        title: str,
        message: str,
        metadata: Optional[dict],
    ) -> Notification:
        """Tạo notification mới và commit."""

    @abstractmethod
    def get_notification_for_owner(self, *, notification_id: int, user_id: int) -> Optional[Notification]:
        """Lấy notification theo owner để enforce ownership."""

    @abstractmethod
    def mark_as_read(self, *, notification: Notification) -> Notification:
        """Đánh dấu notification đã đọc và commit."""

    @abstractmethod
    def mark_all_as_read(self, *, user_id: int) -> int:
        """Đánh dấu toàn bộ notifications chưa đọc của user thành đã đọc, trả về số bản ghi đã cập nhật."""

    @abstractmethod
    def find_recent_due_soon_duplicate(
        self,
        *,
        user_id: int,
        todo_id: int,
        due_date: datetime,
        lookback_minutes: int,
    ) -> Optional[Notification]:
        """Tìm notification due_soon trùng trong khoảng thời gian lookback để tránh duplicate."""

    @abstractmethod
    def get_todo_by_id_for_owner(self, *, todo_id: int, owner_id: int) -> Optional[Todo]:
        """Lấy todo theo owner phục vụ E2E/internal workflow."""
