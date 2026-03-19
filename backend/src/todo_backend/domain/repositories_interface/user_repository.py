#D:\Todos\thangtm25-Todos\Todos\backend\src\todo_backend\domain\repositories_interface\user_repository.py
from abc import ABC, abstractmethod
from typing import List, Optional

from todo_backend.domain.entities.models import Users


class UserRepository(ABC):
    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[Users]:
        pass

    @abstractmethod
    def update_info(self, user_id: int, email: Optional[str], first_name: Optional[str],
                    last_name: Optional[str], phone_number: Optional[int]) -> Optional[Users]:
        pass

    @abstractmethod
    def update_password(self, user_id: int, hashed_password: str) -> bool:
        pass

    @abstractmethod
    def get_all(self) -> List[Users]:
        pass

    @abstractmethod
    def delete(self, user_id: int) -> bool:
        pass

    @abstractmethod
    def toggle_active(self, user_id: int) -> bool:
        pass