from typing import Dict, List, Optional, Tuple

from todo_backend.domain.entities.models import ChatMessage, ChatThread


class ChatRepository:
    def create_thread(self, owner_id: int, thread_id: str, title: Optional[str] = None) -> ChatThread:
        raise NotImplementedError

    def get_thread(self, owner_id: int, thread_id: str) -> Optional[ChatThread]:
        raise NotImplementedError

    def list_threads(self, owner_id: int, limit: int, offset: int) -> Tuple[List[Dict], int]:
        raise NotImplementedError

    def soft_delete_thread(self, owner_id: int, thread_id: str) -> bool:
        raise NotImplementedError

    def add_message(
        self,
        owner_id: int,
        thread_id: str,
        role: str,
        content: str,
        metadata_json: Optional[str] = None,
    ) -> ChatMessage:
        raise NotImplementedError

    def list_messages(self, owner_id: int, thread_id: str, limit: int, offset: int) -> List[ChatMessage]:
        raise NotImplementedError
