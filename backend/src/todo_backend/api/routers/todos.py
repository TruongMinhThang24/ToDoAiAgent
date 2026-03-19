#D:\Todos\thangtm25-Todos\Todos\backend\src\todo_backend\api\routers\todos.py
import logging
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from todo_backend.api.schemas.todos_schema import TodoRequest, TodoResponse
from todo_backend.app.usecases.todos import TodoUseCases
from todo_backend.infrastructure.database.database import sessionLocal
from todo_backend.infrastructure.repositories.todo_repository_impl import \
    TodoRepositoryImpl

from .auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/todos", tags=["todos"])

# Dependency
def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.post("/", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(
    user: user_dependency,
    db: db_dependency,
    todo_request: TodoRequest
):
    if user is None:
        logging.warning(f" Unauthorized attempt to create todo")
        raise HTTPException(status_code=401, detail="Unauthorized")

    logging.info(f"Creating a new todo for user ID: {user['id']}")
    usecase = TodoUseCases(TodoRepositoryImpl(db))
    todo = usecase.create_todo(
        title=todo_request.title,
        description=todo_request.description,
        priority=todo_request.priority,
        owner_id=user["id"],
        
        due_date=todo_request.due_date
    )
    logger.info(f"TODO created successfully with ID: {todo.id}")
    return todo
    

@router.get("/", response_model=list[TodoResponse])
async def get_all_todos(user: user_dependency, db: db_dependency):
    if user is None:
        logger.warning("Unauthorized access attempt to fetch all TODOs")
        raise HTTPException(status_code=401, detail="Unauthorized")

    logger.info(f"Fetching all TODOs for user ID: {user['id']}")
    usecase = TodoUseCases(TodoRepositoryImpl(db))
    todos = usecase.get_all_todos(owner_id=user["id"])
    logger.info(f"Fetched {len(todos)} TODOs for user ID: {user['id']}")
    return todos


@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo_by_id(
    user: user_dependency,
    db: db_dependency,
    todo_id: int = Path(gt=0)
):
    if user is None:
        logger.warning("Unauthorized access attempt to fetch a TODO by ID")
        raise HTTPException(status_code=401, detail="Unauthorized")

    logger.info(f"Fetching TODO with ID: {todo_id} for user ID: {user['id']}")
    usecase = TodoUseCases(TodoRepositoryImpl(db))
    todo = usecase.get_todo_by_id(todo_id=todo_id, owner_id=user["id"])
    if not todo:
        logger.warning(f"TODO with ID {todo_id} not found for user ID: {user['id']}")
        raise HTTPException(status_code=404, detail="Todo not found")
    logger.info(f"TODO with ID {todo_id} fetched successfully for user ID: {user['id']}")
    return todo


@router.put("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
    user: user_dependency,
    db: db_dependency,
    todo_id: int = Path(gt=0),
    todo_request: TodoRequest = Depends()
):
    if user is None:
        logger.warning("Unauthorized access attempt to update a TODO")
        raise HTTPException(status_code=401, detail="Unauthorized")

    logger.info(f"Updating TODO with ID: {todo_id} for user ID: {user['id']}")
    usecase = TodoUseCases(TodoRepositoryImpl(db))
    usecase.update_todo(
        todo_id=todo_id,
        owner_id=user["id"],
        title=todo_request.title,
        description=todo_request.description,
        priority=todo_request.priority,
        completed=todo_request.completed,
        due_date=todo_request.due_date
    )
    logger.info(f"TODO with ID {todo_id} updated successfully for user ID: {user['id']}")


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    user: user_dependency,
    db: db_dependency,
    todo_id: int = Path(gt=0)
):
    if user is None:
        logger.warning("Unauthorized access attempt to delete a TODO")
        raise HTTPException(status_code=401, detail="Unauthorized")

    logger.info(f"Deleting TODO with ID: {todo_id} for user ID: {user['id']}")
    usecase = TodoUseCases(TodoRepositoryImpl(db))
    success = usecase.delete_todo(todo_id=todo_id, owner_id=user["id"])
    if not success:
        logger.warning(f"TODO with ID {todo_id} not found for user ID: {user['id']}")
        raise HTTPException(status_code=404, detail="Todo not found")
    logger.info(f"TODO with ID {todo_id} deleted successfully for user ID: {user['id']}")


@router.get("/search/", response_model=list[TodoResponse])
async def search_todos(
    user: user_dependency,
    db: db_dependency,
    title: Optional[str] = None,
    completed: Optional[bool] = None
):
    if user is None:
        logger.warning("Unauthorized access attempt to search TODOs")
        raise HTTPException(status_code=401, detail="Unauthorized")

    logger.info(f"Searching TODOs for user ID: {user['id']} with title: {title} and complete status: {completed}")
    usecase = TodoUseCases(TodoRepositoryImpl(db))
    todos = usecase.search_todos(owner_id=user["id"], title=title, completed=completed)

    if not todos:
        logger.warning(f"No TODOs found for user ID: {user['id']} with the given criteria")
        raise HTTPException(status_code=404, detail="No todos found with the given criteria")

    logger.info(f"Found {len(todos)} TODOs for user ID: {user['id']} matching the search criteria")
    return todos