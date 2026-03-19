#D:\Todos\thangtm25-Todos\Todos\backend\src\todo_backend\infrastructure\repositories\user_auth_repository_impl.py
from sqlalchemy.orm import Session

from todo_backend.domain.entities.models import Users
from todo_backend.domain.repositories_interface.user_auth_repository import \
    UserAuthRepository


class UserAuthRepositoryImpl(UserAuthRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_username(self, username: str) -> Users:
        return self.db.query(Users).filter(Users.username == username).first()

    def create_user(self, user_data: dict) -> Users:
        new_user = Users(
            email=user_data["email"],
            username=user_data["username"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            role=user_data["role"],
            hashed_password=user_data["hashed_password"],
            is_active=True,
            phone_number=user_data.get("phone_number")
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user
    def update_password(self, username: str, new_hashed_password: str) -> None:
        user = self.get_by_username(username)
        if user:
            user.hashed_password = new_hashed_password
            self.db.commit()
