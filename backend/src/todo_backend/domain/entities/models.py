#D:\Todos\thangtm25-Todos\Todos\backend\src\todo_backend\domain\entities\models.py
import logging
from datetime import datetime

from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Index, Integer,
                        String, Text, event)
from todo_backend.infrastructure.database.database import Base

logger = logging.getLogger(__name__)
class Users(Base):
    logger.info("Initializing Users model")
    __tablename__ = "users"  # Sửa ở đây

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String , unique = True)
    username = Column(String , unique = True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)
    phone_number = Column(String, nullable=True)
    

class Todo(Base):
    logger.info("Initializing Todo model")
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer, default=1)
    completed = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    due_date = Column(DateTime, nullable=True)


class ChatThread(Base):
    __tablename__ = "chat_threads"

    # Giữ tương thích với thread_id dạng string hiện có
    id = Column(String, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(String, ForeignKey("chat_threads.id"), nullable=False, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    role = Column(String, nullable=False)  # user | assistant | system
    content = Column(Text, nullable=False)
    metadata_json = Column("metadata", Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


Index("ix_chat_messages_owner_thread_created", ChatMessage.owner_id, ChatMessage.thread_id, ChatMessage.created_at)

# Sử dụng SQLAlchemy Events để log các sự kiện
@event.listens_for(Users, "after_insert")
def log_user_insert(mapper, connection, target):
    logger.info(f"New user created: ID={target.id}, username={target.username}, email={target.email}")

@event.listens_for(Users, "after_update")
def log_user_update(mapper, connection, target):
    logger.info(f"User updated: ID={target.id}, username={target.username}")

@event.listens_for(Users, "after_delete")
def log_user_delete(mapper, connection, target):
    logger.info(f"User deleted: ID={target.id}, username={target.username}")

@event.listens_for(Todo, "after_insert")
def log_todo_insert(mapper, connection, target):
    logger.info(f"New TODO created: ID={target.id}, title={target.title}, owner_id={target.owner_id}")

@event.listens_for(Todo, "after_update")
def log_todo_update(mapper, connection, target):
    logger.info(f"TODO updated: ID={target.id}, title={target.title}")

@event.listens_for(Todo, "after_delete")
def log_todo_delete(mapper, connection, target):
    logger.info(f"TODO deleted: ID={target.id}, title={target.title}")