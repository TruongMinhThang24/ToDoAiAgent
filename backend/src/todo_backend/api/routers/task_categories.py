import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from todo_backend.api.schemas.task_categories_schema import (
    TaskPriorityCreateRequest,
    TaskPriorityResponse,
    TaskPriorityUpdateRequest,
    TaskStatusCreateRequest,
    TaskStatusResponse,
    TaskStatusUpdateRequest,
)
from todo_backend.domain.entities.models import TaskPriority, TaskStatus
from todo_backend.infrastructure.database.database import sessionLocal

from .auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/task-categories", tags=["task-categories"])


def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/statuses", response_model=list[TaskStatusResponse])
async def get_statuses(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    items = (
        db.query(TaskStatus)
        .filter(TaskStatus.owner_id == user["id"])
        .order_by(TaskStatus.order_index.asc(), TaskStatus.id.asc())
        .all()
    )
    return items


@router.post("/statuses", response_model=TaskStatusResponse, status_code=status.HTTP_201_CREATED)
async def create_status(user: user_dependency, db: db_dependency, payload: TaskStatusCreateRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Status name is required")

    duplicate = (
        db.query(TaskStatus)
        .filter(TaskStatus.owner_id == user["id"], TaskStatus.name.ilike(name))
        .first()
    )
    if duplicate:
        raise HTTPException(status_code=409, detail="Status already exists")

    next_order = db.query(TaskStatus).filter(TaskStatus.owner_id == user["id"]).count() + 1
    entity = TaskStatus(name=name, owner_id=user["id"], order_index=next_order)
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


@router.put("/statuses/{status_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_status(
    user: user_dependency,
    db: db_dependency,
    payload: TaskStatusUpdateRequest,
    status_id: int = Path(gt=0),
):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    item = (
        db.query(TaskStatus)
        .filter(TaskStatus.id == status_id, TaskStatus.owner_id == user["id"])
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Task status not found")

    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Status name is required")

    item.name = name
    db.commit()


@router.delete("/statuses/{status_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_status(user: user_dependency, db: db_dependency, status_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    item = (
        db.query(TaskStatus)
        .filter(TaskStatus.id == status_id, TaskStatus.owner_id == user["id"])
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Task status not found")

    db.delete(item)
    db.commit()


@router.get("/priorities", response_model=list[TaskPriorityResponse])
async def get_priorities(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    items = (
        db.query(TaskPriority)
        .filter(TaskPriority.owner_id == user["id"])
        .order_by(TaskPriority.order_index.asc(), TaskPriority.id.asc())
        .all()
    )
    return items


@router.post("/priorities", response_model=TaskPriorityResponse, status_code=status.HTTP_201_CREATED)
async def create_priority(user: user_dependency, db: db_dependency, payload: TaskPriorityCreateRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Priority name is required")
    if payload.level < 1:
        raise HTTPException(status_code=400, detail="Priority level must be >= 1")

    duplicate = (
        db.query(TaskPriority)
        .filter(TaskPriority.owner_id == user["id"], TaskPriority.name.ilike(name))
        .first()
    )
    if duplicate:
        raise HTTPException(status_code=409, detail="Priority already exists")

    next_order = db.query(TaskPriority).filter(TaskPriority.owner_id == user["id"]).count() + 1
    entity = TaskPriority(name=name, level=payload.level, owner_id=user["id"], order_index=next_order)
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


@router.put("/priorities/{priority_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_priority(
    user: user_dependency,
    db: db_dependency,
    payload: TaskPriorityUpdateRequest,
    priority_id: int = Path(gt=0),
):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    item = (
        db.query(TaskPriority)
        .filter(TaskPriority.id == priority_id, TaskPriority.owner_id == user["id"])
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Task priority not found")

    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Priority name is required")
    if payload.level < 1:
        raise HTTPException(status_code=400, detail="Priority level must be >= 1")

    item.name = name
    item.level = payload.level
    db.commit()


@router.delete("/priorities/{priority_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_priority(user: user_dependency, db: db_dependency, priority_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    item = (
        db.query(TaskPriority)
        .filter(TaskPriority.id == priority_id, TaskPriority.owner_id == user["id"])
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Task priority not found")

    db.delete(item)
    db.commit()
