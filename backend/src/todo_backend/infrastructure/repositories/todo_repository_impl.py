#D:\Todos\thangtm25-Todos\Todos\backend\src\todo_backend\infrastructure\repositories\todo_repository_impl.py
from typing import Any, List, Optional

from sqlalchemy.orm import Session
from datetime import datetime
from todo_backend.domain.entities.models import Todo
from todo_backend.domain.repositories_interface.todo_repository import \
    TodoRepository


class TodoRepositoryImpl(TodoRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, todo: Todo) -> Todo:
        if todo.status == "completed":
            todo.completed = True
        self.db.add(todo)
        self.db.commit()
        self.db.refresh(todo)
        return todo

    def get_all_by_owner(self, owner_id: int) -> List[Todo]:
        return self.db.query(Todo).filter(Todo.owner_id == owner_id).all()

    def get_by_id_and_owner(self, todo_id: int, owner_id: int) -> Optional[Todo]:
        return self.db.query(Todo).filter(Todo.id == todo_id, Todo.owner_id == owner_id).first()

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
        todo = self.get_by_id_and_owner(todo_id, owner_id)
        if todo:
            todo.title = title
            todo.description = description
            todo.priority = priority
            normalized_status = "completed" if completed else status
            todo.status = normalized_status
            todo.completed = normalized_status == "completed"
            todo.due_date = due_date
            todo.thumbnail_url = thumbnail_url
            todo.is_vital = is_vital
            todo.checklist_data = checklist_data
            self.db.commit()
            return True
        return False

    def delete(self, todo_id: int, owner_id: int) -> bool:
        todo = self.get_by_id_and_owner(todo_id, owner_id)
        if todo:
            self.db.delete(todo)
            self.db.commit()
            return True
        return False

    def search(self, owner_id: int, title: Optional[str], completed: Optional[bool]) -> List[Todo]:
        query = self.db.query(Todo).filter(Todo.owner_id == owner_id)
        if title:
            query = query.filter(Todo.title.ilike(f"%{title}%"))
        if completed is not None:
            query = query.filter(Todo.completed == completed)
        return query.all()
    def get_all(self) -> List[Todo]:
        return self.db.query(Todo).all()

    def delete_by_admin(self, todo_id: int) -> bool:
        todo = self.db.query(Todo).filter(Todo.id == todo_id).first()
        if todo:
            self.db.delete(todo)
            self.db.commit()
            return True
        return False

    def toggle_complete(self, todo_id: int) -> bool:
        todo = self.db.query(Todo).filter(Todo.id == todo_id).first()
        if todo:
            todo.completed = not todo.completed
            self.db.commit()
            return True
        return False