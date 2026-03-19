#D:\Todos\thangtm25-Todos\Todos\backend\src\todo_backend\domain\repositories_interface\todo_repository.py
from typing import List, Optional

from todo_backend.domain.entities.models import Todo


class TodoRepository:
    def create(self, todo: Todo) -> Todo:
        raise NotImplementedError

    def get_all_by_owner(self, owner_id: int) -> List[Todo]:
        raise NotImplementedError

    def get_by_id_and_owner(self, todo_id: int, owner_id: int) -> Optional[Todo]:
        raise NotImplementedError

    def update(self, todo_id: int, owner_id: int, title: str, description: str, priority: int, completed: bool) -> bool:
        raise NotImplementedError

    def delete(self, todo_id: int, owner_id: int) -> bool:
        raise NotImplementedError

    def search(self, owner_id: int, title: Optional[str], completed: Optional[bool]) -> List[Todo]:
        raise NotImplementedError