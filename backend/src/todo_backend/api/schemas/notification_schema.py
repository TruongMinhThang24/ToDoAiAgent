from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class NotificationItemResponse(BaseModel):
    id: int
    user_id: int
    type: str
    title: str
    message: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    is_read: bool
    created_at: Optional[datetime] = None
    read_at: Optional[datetime] = None


class NotificationListResponse(BaseModel):
    items: list[NotificationItemResponse]
    total: int
    limit: int
    offset: int


class UnreadCountResponse(BaseModel):
    unread_count: int


class MarkAllReadResponse(BaseModel):
    marked_count: int
    unread_count: int


class NotificationEventResponse(BaseModel):
    event: str
    notification: NotificationItemResponse
    unread_count: int
    created_at: Optional[datetime] = None
