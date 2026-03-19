#D:\Todos\thangtm25-Todos\Todos\backend\src\todo_backend\api\schemas\chat_schema.py
from typing import Optional
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

class AddDocumentRequest(BaseModel):
    text: str