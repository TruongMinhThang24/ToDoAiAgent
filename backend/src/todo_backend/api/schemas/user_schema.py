#D:\Todos\thangtm25-Todos\Todos\backend\src\todo_backend\api\schemas\user_schema.py
from typing import Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class UserVerification(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    password: str = Field(
        validation_alias=AliasChoices("password", "currentPassword", "current_password", "old_password")
    )
    new_password: str = Field(
        min_length=6,
        validation_alias=AliasChoices("new_password", "newPassword"),
    )

class UserUpdateRequest(BaseModel):
    email: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    first_name: str
    last_name: str
    is_active: bool
    role: str
    phone_number: Optional[str]

    
    class Config:
            from_attributes = True
