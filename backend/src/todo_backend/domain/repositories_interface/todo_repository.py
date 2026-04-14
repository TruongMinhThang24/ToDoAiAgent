#D:\Todos\thangtm25-Todos\Todos\backend\src\todo_backend\domain\repositories_interface\todo_repository.py
from datetime import datetime
from typing import Any, List, Optional

from todo_backend.domain.entities.models import Todo


class TodoRepository:
    def create(self, todo: Todo) -> Todo:
        raise NotImplementedError

    def get_all_by_owner(self, owner_id: int) -> List[Todo]:
        raise NotImplementedError

    def get_by_id_and_owner(self, todo_id: int, owner_id: int) -> Optional[Todo]:
        raise NotImplementedError

    def update(
        self,
        todo_id: int,
        owner_id: int,
        title: str,
        description: str,
        priority: int,
        completed: bool,
        due_date: Optional[datetime] = None,
        status: str = "not_started",
        thumbnail_url: Optional[str] = None,
        is_vital: bool = False,
        checklist_data: Optional[list[dict[str, Any]]] = None,
    ) -> bool:
        raise NotImplementedError

    def delete(self, todo_id: int, owner_id: int) -> bool:
        raise NotImplementedError

    def search(self, owner_id: int, title: Optional[str], completed: Optional[bool]) -> List[Todo]:
        raise NotImplementedError