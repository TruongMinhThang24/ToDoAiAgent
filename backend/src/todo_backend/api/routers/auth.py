#D:\Todos\thangtm25-Todos\Todos\backend\src\todo_backend\api\routers\auth.py
import logging
import secrets
from datetime import timedelta
from typing import Annotated
from jose import JWTError, jwt
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from todo_backend.api.schemas.auth_schema import CreateUserRequest, Token , CreateForUserRequest
from todo_backend.app.usecases.auth import AuthUseCases
from todo_backend.config.setting import settings
from todo_backend.domain.entities.models import Users
from todo_backend.infrastructure.database.database import sessionLocal
from todo_backend.infrastructure.repositories.user_auth_repository_impl import \
    UserAuthRepositoryImpl

# Config (nên load từ .env)

logger = logging.getLogger(__name__)
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

router = APIRouter(prefix="/auth", tags=["auth"])

# Dependency
def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    db: db_dependency,
    create_user_request: CreateUserRequest
):
    usecase = AuthUseCases(UserAuthRepositoryImpl(db))
    user = usecase.create_user(create_user_request.dict())
    return {"message": "User created", "user_id": user.id}

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def create_for_user(
    db: db_dependency,
    create_for_user_request: CreateForUserRequest
):
    user_data = create_for_user_request.dict()
    user_data['role'] = 'user'

    usecase = AuthUseCases(UserAuthRepositoryImpl(db))
    user = usecase.create_user(user_data)
    return {"message": "User created", "user_id": user.id}

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: db_dependency,
    response: Response,
):
    usecase = AuthUseCases(UserAuthRepositoryImpl(db))
    user = usecase.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Cookie age bám theo TTL của access token để đồng bộ thời gian sống.
    access_token_ttl = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = usecase.create_access_token(user.username, user.id, user.role, access_token_ttl)

    # SECURITY: Lưu JWT trong HttpOnly cookie để giảm rủi ro token bị đánh cắp qua XSS.
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,  # Dev localhost; production nên dùng True theo env.
        samesite="lax",
        max_age=int(access_token_ttl.total_seconds()),
    )

    # SECURITY: CSRF token (double-submit cookie) để frontend đính kèm header X-CSRF-Token.
    csrf_token = secrets.token_urlsafe(32)
    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        httponly=False,
        secure=False,
        samesite="lax",
        max_age=int(access_token_ttl.total_seconds()),
    )

    return {"access_token": token, "token_type": "bearer"}


async def validate_token_and_get_user(token: str, db: Session) -> dict:
    """
    Hàm này chỉ giải mã token và lấy user.
    Nó được dùng chung cho cả HTTP và WebSocket.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        role: str = payload.get("role")
        if username is None or user_id is None:
            raise credentials_exception
        
        user = db.query(Users).filter(Users.id == user_id).first()
        if user is None:
            raise credentials_exception
        
        # Trả về đầy đủ thông tin user
        return {
            "username": username, 
            "id": user_id, 
            "role": role,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone_number": user.phone_number
        }
    except JWTError:
        raise credentials_exception
    except Exception as e:
        logger.error(f"Error validating token: {e}")
        raise credentials_exception

# --- HÀM DEPENDENCY MỚI CHO HTTP ---
async def get_current_user(
    request: Request,
    db: db_dependency
):
    """
    Đây là dependency CHỈ DÙNG CHO HTTP.
    Nó đọc access token từ HttpOnly cookie thay vì Authorization header.
    """
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return await validate_token_and_get_user(token, db)


@router.post("/logout")
async def logout(response: Response):
    """
    SECURITY: Xóa HttpOnly cookie chứa JWT khi logout để kết thúc phiên đăng nhập.
    """
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=False,
        samesite="lax",
    )
    response.delete_cookie(
        key="csrf_token",
        httponly=False,
        secure=False,
        samesite="lax",
    )
    return {"message": "Logged out successfully"}

# --- SỬA LẠI ENDPOINT /me ---
@router.get("/me")
async def get_me(user: Annotated[dict, Depends(get_current_user)]):
    """
    Endpoint /me bây giờ chỉ cần phụ thuộc vào
    get_current_user để lấy thông tin.
    """
    return user