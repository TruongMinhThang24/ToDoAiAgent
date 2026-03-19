#D:\Todos\thangtm25-Todos\Todos\backend\src\todo_backend\api\routers\user.py
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from todo_backend.api.schemas.user_schema import (UserResponse,
                                                  UserUpdateRequest,
                                                  UserVerification)
from todo_backend.app.usecases.user import UserUseCases
from todo_backend.infrastructure.database.database import sessionLocal
from todo_backend.infrastructure.repositories.user_repository_impl import \
    UserRepositoryImpl

from .auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/user", tags=["user"])

# Dependency
def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/", response_model=UserResponse)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        logger.warning(f" Unauthorized attempt to access user profile")
        raise HTTPException(status_code=401, detail="Unauthorized")

    logger.info(f"Fetching user profile for user ID: {user['id']}")
    usecase = UserUseCases(UserRepositoryImpl(db))
    user_model = usecase.get_user(user["id"])
    if not user_model:
        logger.warning(f"User with ID: {user['id']} not found")
        raise HTTPException(status_code=404, detail="User not found")
    logger.info(f"User profile fetched successfully for user ID: {user['id']}")
    return user_model


@router.put("/update", response_model=UserResponse)
async def update_user_info(
    user: user_dependency,
    db: db_dependency,
    update_request: UserUpdateRequest
):
    if user is None:
        logger.warning(f" Unauthorized attempt to update user profile")
        raise HTTPException(status_code=401, detail="Unauthorized")
    logger.info(f"Updating user profile for user ID: {user['id']}")
    usecase = UserUseCases(UserRepositoryImpl(db))
    updated_user = usecase.update_user_info(
        user_id=user["id"],
        email=update_request.email,
        first_name=update_request.first_name,
        last_name=update_request.last_name,
        phone_number=update_request.phone_number
    )

    if not updated_user:
        logger.warning(f"User with ID: {user['id']} not found")
        raise HTTPException(status_code=404, detail="User not found")
    logger.info("User profile updated successfully for user ID: {user['id']}")
    return updated_user


@router.put("/change_password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    user: user_dependency,
    db: db_dependency,
    user_verification: UserVerification
):
    if user is None:
        logger.warning(f" Unauthorized attempt to change password")
        raise HTTPException(status_code=401, detail="Unauthorized")
    logger.info(f"Attempting to change password for user ID: {user['id']}")
    usecase = UserUseCases(UserRepositoryImpl(db))
    success = usecase.change_password(
        user_id=user["id"],
        old_password=user_verification.password,
        new_password=user_verification.new_password
    )

    if not success:
        logger.warning(f"Incorrect password provided for user ID: {user['id']}")
        raise HTTPException(status_code=401, detail="Incorrect password")
    logger.info(f"Password changed successfully for user ID: {user['id']}")