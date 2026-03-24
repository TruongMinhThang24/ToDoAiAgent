#D:\Todos\thangtm25-Todos\Todos\backend\src\todo_backend\api\schemas\chat_schema.py
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class AgentChatReponse(BaseModel):
    friendly_message: str
    thread_id: str
    needs_clarification: bool = False
    clarification_prompt: Optional[str] = None
    class Config: 
        from_attributes = True
    
    
class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str]


class CreateThreadRequest(BaseModel):
    title: Optional[str] = None


class ThreadItemResponse(BaseModel):
    thread_id: str
    title: Optional[str] = None
    last_message: str = ""
    updated_at: datetime
    created_at: datetime
    message_count: int = 0


class ThreadListResponse(BaseModel):
    items: List[ThreadItemResponse]
    total: int
    limit: int
    offset: int


class ThreadMessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime


class ThreadMessageListResponse(BaseModel):
    thread_id: str
    items: List[ThreadMessageResponse]
    limit: int
    offset: int

class AgentExecuteRequest(BaseModel):
    action_type: str
    user_prompt: str
    metadata: Optional[dict] = {}

class AddDocumentRequest(BaseModel):
    text: str