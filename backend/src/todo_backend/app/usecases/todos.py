#D:\Todos\thangtm25-Todos\Todos\backend\src\todo_backend\app\usecases\todos.py
import logging
from datetime import datetime
from typing import List, Optional

from todo_backend.domain.entities.models import Todo
from todo_backend.domain.repositories_interface.todo_repository import \
    TodoRepository

logger = logging.getLogger(__name__)

class TodoUseCases:
    def __init__(self, todo_repository: TodoRepository):
        self.todo_repository = todo_repository

    def create_todo(self, title: str, description: str, priority: int, owner_id: int , due_date: Optional[datetime] = None) -> Todo:
        new_todo = Todo(
            title=title,
            description=description,
            priority=priority,
            completed=False,
            owner_id=owner_id,
            due_date=due_date # Thêm due_date
        )
        # return self.todo_repository.create(new_todo) 
        created_todo = self.todo_repository.create(new_todo)
        logger.info(f"TODO created successfully with ID: {created_todo.id}")
        return created_todo

    def get_all_todos(self, owner_id: int) -> List[Todo]:
        logger.info(f"Fetching all TODOs for owner ID: {owner_id}")
        todos = self.todo_repository.get_all_by_owner(owner_id)
        logger.info(f"Fetched {len(todos)} TODOs for owner ID: {owner_id}")
        return todos

    def get_todo_by_id(self, todo_id: int, owner_id: int) -> Optional[Todo]:
        logger.info(f"Fetching TODO with ID: {todo_id} for owner ID: {owner_id}")
        todo = self.todo_repository.get_by_id_and_owner(todo_id, owner_id)
        if todo:
            logger.info(f"TODO found: {todo}")
        else:
            logger.warning(f"TODO with ID {todo_id} not found for owner ID: {owner_id}")
        return todo

    def update_todo(self, todo_id: int, owner_id: int, title: str, description: str, priority: int, completed: bool, due_date: Optional[datetime] = None):
        logger.info(f"Updating TODO with ID: {todo_id} for owner ID: {owner_id}")
        updated_todo = self.todo_repository.update(todo_id, owner_id, title, description, priority, completed, due_date) # Thêm due_date
        if updated_todo:
            logger.info(f"TODO updated successfully with ID: {todo_id}")
        else:
            logger.warning(f"Failed to update TODO with ID: {todo_id} for owner ID: {owner_id}")
        return updated_todo

    def delete_todo(self, todo_id: int, owner_id: int):
        logger.info(f"Deleting TODO with ID: {todo_id} for owner ID: {owner_id}")
        try:
            success = self.todo_repository.delete(todo_id, owner_id)
            if success:
                logger.info(f"TODO deleted successfully with ID: {todo_id}")
            else:
                logger.warning(f"Failed to delete TODO with ID: {todo_id} for owner ID: {owner_id}")
            return success
        except Exception as e:
            logger.error(f"Error deleting TODO with ID: {todo_id} for owner ID: {owner_id}. Error: {str(e)}")
            return False

    def search_todos(self, owner_id: int, title: Optional[str], completed: Optional[bool]) -> List[Todo]:
        logger.info(f"Searching TODOs for owner ID: {owner_id} with title: {title} and complete status: {completed}")
        todos = self.todo_repository.search(owner_id, title, completed)
        logger.info(f"Found {len(todos)} TODOs matching search criteria for owner ID: {owner_id}")
        return todos

    def query_todos(
        self,
        owner_id: int,
        q: Optional[str],
        status: str,
        view: str,
        sort_by: str,
        sort_order: str,
        page: int,
        page_size: int,
    ) -> tuple[List[Todo], int]:
        logger.info(
            "Querying todos for owner_id=%s with q=%s, status=%s, view=%s, sort_by=%s, sort_order=%s, page=%s, page_size=%s",
            owner_id,
            q,
            status,
            view,
            sort_by,
            sort_order,
            page,
            page_size,
        )

        todos = self.todo_repository.get_all_by_owner(owner_id)

        # Search (case-insensitive, title + description)
        if q:
            keyword = q.strip().lower()
            if keyword:
                todos = [
                    todo for todo in todos
                    if keyword in (todo.title or "").lower()
                    or keyword in (todo.description or "").lower()
                ]

        # View filter
        if view == "inbox":
            todos = [todo for todo in todos if not todo.completed]
        elif view == "archived":
            todos = [todo for todo in todos if todo.completed]

        # Status filter
        now = datetime.now()
        if status == "active":
            todos = [todo for todo in todos if not todo.completed]
        elif status == "completed":
            todos = [todo for todo in todos if todo.completed]
        elif status == "overdue":
            todos = [
                todo
                for todo in todos
                if (not todo.completed) and (todo.due_date is not None) and (todo.due_date < now)
            ]

        # Sort
        reverse = sort_order == "desc"
        if sort_by == "due_date":
            if reverse:
                # Due date DESC: farthest due date first, None last
                todos.sort(
                    key=lambda todo: (
                        todo.due_date is None,
                        -(todo.due_date.timestamp()) if todo.due_date else float("inf"),
                    )
                )
            else:
                # Due date ASC: nearest due date first, None last
                todos.sort(
                    key=lambda todo: (
                        todo.due_date is None,
                        todo.due_date.timestamp() if todo.due_date else float("inf"),
                    )
                )
        elif sort_by == "priority":
            todos.sort(key=lambda todo: todo.priority or 0, reverse=reverse)
        else:
            # created_at replacement by id (newer id = newer todo)
            todos.sort(key=lambda todo: todo.id or 0, reverse=reverse)

        total = len(todos)

        # Pagination
        start = (page - 1) * page_size
        end = start + page_size
        items = todos[start:end]

        logger.info("Query result for owner_id=%s: total=%s, returned=%s", owner_id, total, len(items))
        return items, total
