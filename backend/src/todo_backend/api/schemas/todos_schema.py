#D:\Todos\thangtm25-Todos\Todos\backend\src\todo_backend\api\schemas\todos_schema.py
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator
from typing import Literal


class TodoBasePayload(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = ""
    priority: int = Field(ge=1, le=5)
    completed: bool = False
    due_date: Optional[datetime] = None
    status: Literal["not_started", "in_progress", "completed"] = "not_started"
    thumbnail_url: Optional[str] = None
    is_vital: bool = False
    checklist_data: Optional[list[dict[str, Any]]] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("title must not be empty")
        return normalized

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str) -> str:
        return (value or "").strip()

    @field_validator("thumbnail_url")
    @classmethod
    def reject_blob_thumbnail_url(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            return None
        if normalized.startswith("blob:"):
            raise ValueError("thumbnail_url must be a server-accessible URL")
        return normalized


class TodoRequest(TodoBasePayload):
    pass


class TodoUpdateRequest(TodoBasePayload):
    pass


class TodoResponse(BaseModel):
    id: int
    title: str
    description: str
    priority: int
    completed: bool
    status: Literal["not_started", "in_progress", "completed"]
    thumbnail_url: Optional[str] = None
    is_vital: bool
    checklist_data: Optional[list[dict[str, Any]]] = None
    owner_id: int
    due_date: Optional[datetime] = None
    created_at: datetime


    class Config:
            from_attributes = True


class TodoListResponse(BaseModel):
    items: list[TodoResponse]
    total: int
    page: int
    page_size: int
