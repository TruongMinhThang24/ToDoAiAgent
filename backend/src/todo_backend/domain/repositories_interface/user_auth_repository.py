#D:\Todos\thangtm25-Todos\Todos\backend\src\todo_backend\domain\repositories_interface\user_auth_repository.py
from abc import ABC, abstractmethod
from typing import Optional

from todo_backend.domain.entities.models import Users


class UserAuthRepository(ABC):
    @abstractmethod
    def get_by_username(self, username: str) -> Optional[Users]:
        pass

    @abstractmethod
    def create_user(self, user_data: dict) -> Users:
        pass

    def update_password(self, username: str, new_hashed_password: str) -> None:
        pass