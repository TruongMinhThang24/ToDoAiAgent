from typing import Dict, List, Tuple

from fastapi import HTTPException

from todo_backend.domain.repositories_interface.chat_repository import ChatRepository


class ChatThreadService:
    def __init__(self, repo: ChatRepository, owner_id: int):
        self.repo = repo
        self.owner_id = owner_id

    def ensure_thread(self, thread_id: str) -> None:
        thread = self.repo.get_thread(owner_id=self.owner_id, thread_id=thread_id)
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")

    def create_thread(self, thread_id: str, title: str | None = None):
        return self.repo.create_thread(owner_id=self.owner_id, thread_id=thread_id, title=title)

    def list_threads(self, limit: int, offset: int) -> Tuple[List[Dict], int]:
        return self.repo.list_threads(owner_id=self.owner_id, limit=limit, offset=offset)

    def delete_thread(self, thread_id: str) -> None:
        success = self.repo.soft_delete_thread(owner_id=self.owner_id, thread_id=thread_id)
        if not success:
            raise HTTPException(status_code=404, detail="Thread not found")

    def list_messages(self, thread_id: str, limit: int, offset: int):
        self.ensure_thread(thread_id)
        return self.repo.list_messages(owner_id=self.owner_id, thread_id=thread_id, limit=limit, offset=offset)

    def add_message(self, thread_id: str, role: str, content: str):
        return self.repo.add_message(owner_id=self.owner_id, thread_id=thread_id, role=role, content=content)
