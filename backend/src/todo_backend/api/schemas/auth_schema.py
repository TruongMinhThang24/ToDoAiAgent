#D:\Todos\thangtm25-Todos\Todos\backend\src\todo_backend\api\schemas\auth_schema.py
from pydantic import BaseModel


class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
    phone_number: str = None

class Token(BaseModel):
    access_token: str
    token_type: str

class Config:
    from_attributes = True

class CreateForUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    phone_number: str = None