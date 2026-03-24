#D:\Todos\thangtm25-Todos\Todos\backend\src\todo_backend\api\schemas\todos_schema.py
from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class TodoRequest(BaseModel):
    title: str
    description: str
    priority: int
    completed: Optional[bool] = False
    due_date: Optional[datetime] = None # Thêm due_date
class TodoResponse(BaseModel):
    id: int
    title: str
    description: str
    priority: int
    completed: bool
    owner_id: int
    due_date: Optional[datetime] = None # Thêm due_date


    class Config:
            from_attributes = True


class TodoListResponse(BaseModel):
    items: list[TodoResponse]
    total: int
    page: int
    page_size: int
