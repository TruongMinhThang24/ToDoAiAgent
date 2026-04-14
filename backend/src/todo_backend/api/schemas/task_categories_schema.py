from datetime import datetime

from pydantic import BaseModel


class TaskStatusCreateRequest(BaseModel):
    name: str


class TaskStatusUpdateRequest(BaseModel):
    name: str


class TaskStatusResponse(BaseModel):
    id: int
    name: str
    order_index: int
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class TaskPriorityCreateRequest(BaseModel):
    name: str
    level: int


class TaskPriorityUpdateRequest(BaseModel):
    name: str
    level: int


class TaskPriorityResponse(BaseModel):
    id: int
    name: str
    level: int
    order_index: int
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True
