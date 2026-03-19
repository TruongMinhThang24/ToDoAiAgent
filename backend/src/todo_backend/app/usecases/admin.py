# D:\Todos\thangtm25-Todos\Todos\backend\src\todo_backend\app\usecases\admin.py
import logging
from typing import List, Optional

from todo_backend.domain.entities.models import Todo, Users
from todo_backend.domain.repositories_interface.todo_repository import \
    TodoRepository
from todo_backend.domain.repositories_interface.user_repository import \
    UserRepository

logger = logging.getLogger(__name__)
class AdminUseCases:
    def __init__(self, user_repo: UserRepository, todo_repo: TodoRepository):
        self.user_repo = user_repo
        self.todo_repo = todo_repo
        logger.info

    # --- USER MANAGEMENT ---
    def get_all_users(self) -> List[Users]:
        logger.info("Fetching all users")
        return self.user_repo.get_all()

    def delete_user(self, user_id: int) -> bool:
        logger.info(f"Deleting user with ID: {user_id}")
        return self.user_repo.delete(user_id)

    def toggle_user_active(self, user_id: int) -> bool:
        logger.info(f"Toggling active status for user with ID: {user_id}")
        return self.user_repo.toggle_active(user_id)

    # --- TODO MANAGEMENT ---
    def get_all_todos(self) -> List[Todo]:
        logger.info(f"Fetching all todos for admin")
        return self.todo_repo.get_all()

    def delete_todo(self, todo_id: int) -> bool:
        logger.info(f"Deleting todo with ID: {todo_id}")
        return self.todo_repo.delete_by_admin(todo_id)

    def toggle_todo_complete(self, todo_id: int) -> bool:
        logger.info(f"Toggling complete status for todo with ID: {todo_id}")
        return self.todo_repo.toggle_complete(todo_id)