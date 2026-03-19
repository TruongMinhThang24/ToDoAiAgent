#D:\Todos\thangtm25-Todos\Todos\backend\src\todo_backend\app\usecases\user.py
import logging
from typing import Optional

from passlib.context import CryptContext

from todo_backend.domain.entities.models import Users
from todo_backend.domain.repositories_interface.user_repository import \
    UserRepository

logger = logging.getLogger(__name__)

class UserUseCases:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        self.bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def get_user(self, user_id: int) -> Optional[Users]:
        logger.info(f"Fetching user with ID: {user_id}")
        user = self.user_repository.get_by_id(user_id)
        if user:
            logger.info(f"User found: {user}")
        else:
            logger.warning(f"User with ID {user_id} not found")
        return user
    

    def update_user_info(self, user_id: int, email: Optional[str], first_name: Optional[str],
                         last_name: Optional[str], phone_number: Optional[str]) -> Optional[Users]:
        logger.info(f"Updating user info for user ID: {user_id}")
        updated_user = self.user_repository.update_info(user_id, email, first_name, last_name, phone_number)
        if updated_user:
            logger.info(f"User info updated successfully for user ID: {user_id}")
        else:
            logger.warning(f"Failed to update user info for user ID: {user_id}")
        return updated_user

    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        logger.info(f"Changing password for user ID: {user_id}")
        user = self.user_repository.get_by_id(user_id)
        if not user:
            logger.warning(f"User with ID {user_id} not found")
            return False
        if not self.bcrypt_context.verify(old_password, user.hashed_password):
            logger.warning(f"Old password verification failed for user ID: {user_id}")
            return False
        hashed = self.bcrypt_context.hash(new_password)
        self.user_repository.update_password(user_id, hashed)
        logger.info(f"Password changed successfully for user ID: {user_id}")
        return True