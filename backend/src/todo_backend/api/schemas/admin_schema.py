#D:\Todos\thangtm25-Todos\Todos\backend\src\todo_backend\api\schemas\admin_schema.py
from pydantic import BaseModel


class UpdateUserRequest(BaseModel):
    email: str
    username: str
    first_name: str
    last_name: str
    phone_number: int
    is_active: bool
    role: str

class Config:
    from_attributes = True