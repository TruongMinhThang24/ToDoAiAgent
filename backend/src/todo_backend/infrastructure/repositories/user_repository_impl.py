#D:\Todos\thangtm25-Todos\Todos\backend\src\todo_backend\infrastructure\repositories\user_repository_impl.py
from typing import List, Optional

from sqlalchemy.orm import Session

from todo_backend.domain.entities.models import Users
from todo_backend.domain.repositories_interface.user_repository import \
    UserRepository


class UserRepositoryImpl(UserRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[Users]:
        return self.db.query(Users).filter(Users.id == user_id).first()

    def update_info(self, user_id: int, email: Optional[str], first_name: Optional[str],
                    last_name: Optional[str], phone_number: Optional[int]) -> Optional[Users]:
        user = self.get_by_id(user_id)
        if not user:
            return None
        if email is not None:
            user.email = email
        if first_name is not None:
            user.first_name = first_name
        if last_name is not None:
            user.last_name = last_name
        if phone_number is not None:
            user.phone_number = phone_number
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_password(self, user_id: int, hashed_password: str) -> bool:
        user = self.get_by_id(user_id)
        if user:
            user.hashed_password = hashed_password
            self.db.commit()

    def get_all(self) -> List[Users]:
        return self.db.query(Users).all()

    def delete(self, user_id: int) -> bool:
        user = self.get_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False

    def toggle_active(self, user_id: int) -> bool:
        user = self.get_by_id(user_id)
        if user:
            user.is_active = not user.is_active
            self.db.commit()
            return True
        return False