# D:\Todos\thangtm25-Todos\Todos\backend\src\todo_backend\app\usecases\auth.py
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt
from passlib.context import CryptContext

from todo_backend.config.setting import \
    settings  # hoặc từ infrastructure.config.setting nếu bạn đặt ở đó
from todo_backend.domain.entities.models import Users
from todo_backend.domain.repositories_interface.user_auth_repository import \
    UserAuthRepository

logger = logging.getLogger(__name__)

class AuthUseCases:
    def __init__(self, user_repository: UserAuthRepository):
        self.user_repository = user_repository
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.pwd_context = CryptContext(
        schemes=["argon2", "bcrypt"],
        deprecated=["bcrypt"],  # Đánh dấu bcrypt là không còn được ưa chuộng
        # Cấu hình Argon2 (tùy chọn)
        argon2__rounds=4,  # Số vòng lặp
        argon2__memory_cost=65536,  # 64MB
        argon2__parallelism=4,  # Số luồng
    )
    logger.info("AuthUseCases initialized with Argon2 and bcrypt fallback")

    def create_user(self, user_data: dict) -> Users:
        # Argon2 không có giới hạn 72 byte như bcrypt, nhưng vẫn nên giới hạn độ dài
        password = user_data["password"]
        
        # Hash mật khẩu với Argon2
        hashed_password = self.pwd_context.hash(password)
        logger.info(f"Creating user with username: {user_data['username']}")
        return self.user_repository.create_user({
            **user_data,
            "hashed_password": hashed_password
        })

    def authenticate_user(self, username: str, password: str) -> Optional[Users]:
        user = self.user_repository.get_by_username(username)
        if not user:
            logger.warning(f"User with username: {username} not found")
            return None

        try:
            # Xác thực mật khẩu (tự động kiểm tra cả bcrypt và argon2)
            if not self.pwd_context.verify(password, user.hashed_password):
                logger.warning(f"Invalid credentials for user: {username}")
                return None
                
            # Kiểm tra xem có cần nâng cấp hash không
            if self.pwd_context.needs_update(user.hashed_password):
                logger.info(f"Upgrading password hash for user: {username}")
                # Tạo hash mới với Argon2
                new_hash = self.pwd_context.hash(password)
                # Cập nhật vào DB (cần thêm phương thức update_password)
                self.user_repository.update_password(username, new_hash)
                
            logger.info(f"User: {username} authenticated successfully")
            return user
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return None
    def create_access_token(self, username: str, user_id: int, role: str, expires_delta: timedelta) -> str:
        payload = {
            "sub": username,
            "id": user_id,
            "role": role,
            "exp": datetime.now(timezone.utc) + expires_delta
        }
        logger .info(f"Creating access token for user: {username}")
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)