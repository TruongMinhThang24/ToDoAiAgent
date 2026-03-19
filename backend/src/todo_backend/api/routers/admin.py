import logging
from typing import Annotated

#D:\Todos\thangtm25-Todos\Todos\backend\src\todo_backend\api\routers\admin.py
from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from todo_backend.api.routers.auth import get_current_user
from todo_backend.api.schemas.admin_schema import UpdateUserRequest
from todo_backend.api.schemas.todos_schema import TodoResponse
from todo_backend.api.schemas.user_schema import UserResponse
from todo_backend.app.usecases.admin import AdminUseCases
from todo_backend.infrastructure.database.database import sessionLocal
from todo_backend.infrastructure.repositories.todo_repository_impl import \
    TodoRepositoryImpl
from todo_backend.infrastructure.repositories.user_repository_impl import \
    UserRepositoryImpl

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])

# Dependency
def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


def check_admin(user: dict):
    if user is None or user.get("role") != "admin":
        logger.warning("Unauthorized access attempt")
        raise HTTPException(status_code=401, detail="Admin access required")


@router.get("/user", response_model=list[UserResponse])
async def get_all_users(user: user_dependency, db: db_dependency):
    check_admin(user)
    logger.info("Fetching all users")
    usecase = AdminUseCases(UserRepositoryImpl(db), TodoRepositoryImpl(db))
    return usecase.get_all_users()


@router.delete("/user/{user_id}", status_code=204)
async def delete_user(user: user_dependency, db: db_dependency, user_id: int):
    check_admin(user)
    logger.info(f"Deleting user with ID: {user_id}")
    usecase = AdminUseCases(UserRepositoryImpl(db), TodoRepositoryImpl(db))
    success = usecase.delete_user(user_id)
    if not success:
        logger.warning(f"Failed to delete user, user not found{user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    logger.info(f"User deleted with ID: {user_id} susscessfull")

@router.put("/user/{user_id}", status_code=204)
async def toggle_user_active(user: user_dependency, db: db_dependency, user_id: int):
    check_admin(user)
    logger.info(f"Toggling user active status with ID: {user_id}")
    usecase = AdminUseCases(UserRepositoryImpl(db), TodoRepositoryImpl(db))
    success = usecase.toggle_user_active(user_id)
    if not success:
        logger.warning(f"Failed to toggle user active status, user not found{user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    logger.info(f"Toggled user active status with ID: {user_id} susscessfull")


@router.get("/todo", response_model=list[TodoResponse])
async def get_all_todos(user: user_dependency, db: db_dependency):
    check_admin(user)
    logger.info("Fetching all todos")
    usecase = AdminUseCases(UserRepositoryImpl(db), TodoRepositoryImpl(db))
    todos = usecase.get_all_todos()
    logger.info(f"Fetched {len(todos)} todos")
    return todos

@router.delete("/todo/{todo_id}", status_code=204)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    check_admin(user)
    logger.info(f"Attempting to delete todo with ID: {todo_id}")
    usecase = AdminUseCases(UserRepositoryImpl(db), TodoRepositoryImpl(db))
    success = usecase.delete_todo(todo_id)
    if not success:
        logger.warning(f"Todo with ID {todo_id} not found")
        raise HTTPException(status_code=404, detail="Todo not found")
    logger.info(f"Todo with ID {todo_id} deleted successfully")

@router.put("/todo/{todo_id}", status_code=204)
async def toggle_todo_complete(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    check_admin(user)
    logger.info(f"Toggling complete status for todo with ID: {todo_id}")
    usecase = AdminUseCases(UserRepositoryImpl(db), TodoRepositoryImpl(db))
    success = usecase.toggle_todo_complete(todo_id)
    if not success:
        logger.warning(f"Todo with ID {todo_id} not found")
        raise HTTPException(status_code=404, detail="Todo not found")
    logger.info(f"Todo with ID {todo_id} complete status toggled successfully")