from datetime import datetime
from typing import Dict, List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from todo_backend.domain.entities.models import ChatMessage, ChatThread
from todo_backend.domain.repositories_interface.chat_repository import ChatRepository


class ChatRepositoryImpl(ChatRepository):
    def __init__(self, db: Session):
        self.db = db

    def create_thread(self, owner_id: int, thread_id: str, title: Optional[str] = None) -> ChatThread:
        thread = ChatThread(
            id=thread_id,
            owner_id=owner_id,
            title=title,
            is_deleted=False,
        )
        self.db.add(thread)
        self.db.commit()
        self.db.refresh(thread)
        return thread

    def get_thread(self, owner_id: int, thread_id: str) -> Optional[ChatThread]:
        return (
            self.db.query(ChatThread)
            .filter(
                ChatThread.id == thread_id,
                ChatThread.owner_id == owner_id,
                ChatThread.is_deleted == False,
            )
            .first()
        )

    def list_threads(self, owner_id: int, limit: int, offset: int) -> Tuple[List[Dict], int]:
        base_query = (
            self.db.query(ChatThread)
            .filter(ChatThread.owner_id == owner_id, ChatThread.is_deleted == False)
            .order_by(ChatThread.updated_at.desc())
        )

        total = base_query.count()
        threads = base_query.offset(offset).limit(limit).all()

        items: List[Dict] = []
        for thread in threads:
            last_message = (
                self.db.query(ChatMessage)
                .filter(ChatMessage.thread_id == thread.id, ChatMessage.owner_id == owner_id)
                .order_by(ChatMessage.created_at.desc(), ChatMessage.id.desc())
                .first()
            )
            message_count = (
                self.db.query(func.count(ChatMessage.id))
                .filter(ChatMessage.thread_id == thread.id, ChatMessage.owner_id == owner_id)
                .scalar()
            ) or 0

            items.append(
                {
                    "thread_id": thread.id,
                    "title": thread.title or (last_message.content[:60] if last_message and last_message.content else "New conversation"),
                    "last_message": last_message.content if last_message else "",
                    "updated_at": thread.updated_at,
                    "created_at": thread.created_at,
                    "message_count": message_count,
                }
            )

        return items, total

    def soft_delete_thread(self, owner_id: int, thread_id: str) -> bool:
        thread = self.get_thread(owner_id=owner_id, thread_id=thread_id)
        if not thread:
            return False

        thread.is_deleted = True
        thread.updated_at = datetime.utcnow()
        self.db.commit()
        return True

    def add_message(
        self,
        owner_id: int,
        thread_id: str,
        role: str,
        content: str,
        metadata_json: Optional[str] = None,
    ) -> ChatMessage:
        message = ChatMessage(
            owner_id=owner_id,
            thread_id=thread_id,
            role=role,
            content=content,
            metadata_json=metadata_json,
        )
        self.db.add(message)

        thread = self.get_thread(owner_id=owner_id, thread_id=thread_id)
        if thread:
            thread.updated_at = datetime.utcnow()
            if not thread.title and role == "user" and content:
                thread.title = content[:80]

        self.db.commit()
        self.db.refresh(message)
        return message

    def list_messages(self, owner_id: int, thread_id: str, limit: int, offset: int) -> List[ChatMessage]:
        return (
            self.db.query(ChatMessage)
            .filter(ChatMessage.owner_id == owner_id, ChatMessage.thread_id == thread_id)
            .order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )
