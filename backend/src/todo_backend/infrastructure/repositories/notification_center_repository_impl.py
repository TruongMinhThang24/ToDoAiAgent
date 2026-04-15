from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from todo_backend.domain.entities.models import Notification, Todo
from todo_backend.domain.repositories_interface.notification_center_repository import NotificationCenterRepository


class NotificationCenterRepositoryImpl(NotificationCenterRepository):
    def __init__(self, db: Session):
        self.db = db

    def list_notifications(
        self,
        *,
        user_id: int,
        is_read: Optional[bool],
        limit: int,
        offset: int,
    ) -> tuple[list[Notification], int]:
        query = self.db.query(Notification).filter(Notification.user_id == user_id)
        if is_read is not None:
            query = query.filter(Notification.is_read == is_read)

        total = query.count()
        items = (
            query.order_by(Notification.created_at.desc(), Notification.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return items, total

    def count_unread(self, *, user_id: int) -> int:
        return self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False,
        ).count()

    def create_notification(
        self,
        *,
        user_id: int,
        notification_type: str,
        title: str,
        message: str,
        metadata: Optional[dict],
    ) -> Notification:
        item = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            metadata_json=metadata or {},
            is_read=False,
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def get_notification_for_owner(self, *, notification_id: int, user_id: int) -> Optional[Notification]:
        return self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        ).first()

    def mark_as_read(self, *, notification: Notification) -> Notification:
        if not notification.is_read:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            self.db.add(notification)
            self.db.commit()
            self.db.refresh(notification)
        return notification

    def mark_all_as_read(self, *, user_id: int) -> int:
        unread_items = self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False,
        ).all()

        if not unread_items:
            return 0

        now = datetime.utcnow()
        for item in unread_items:
            item.is_read = True
            item.read_at = now
            self.db.add(item)

        self.db.commit()
        return len(unread_items)

    def find_recent_due_soon_duplicate(
        self,
        *,
        user_id: int,
        todo_id: int,
        due_date: datetime,
        lookback_minutes: int,
    ) -> Optional[Notification]:
        cutoff = datetime.utcnow() - timedelta(minutes=lookback_minutes)
        candidates = self.db.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.type == "todo_due_soon",
                Notification.created_at >= cutoff,
            )
        ).order_by(Notification.created_at.desc()).limit(50).all()

        for item in candidates:
            metadata = item.metadata_json or {}
            if metadata.get("todo_id") == todo_id and metadata.get("due_date") == due_date.isoformat():
                return item

        return None

    def get_todo_by_id_for_owner(self, *, todo_id: int, owner_id: int) -> Optional[Todo]:
        return self.db.query(Todo).filter(Todo.id == todo_id, Todo.owner_id == owner_id).first()
