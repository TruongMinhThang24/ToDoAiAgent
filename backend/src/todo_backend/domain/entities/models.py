#D:\Todos\thangtm25-Todos\Todos\backend\src\todo_backend\domain\entities\models.py
import logging
from datetime import datetime

from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Index, Integer,
                        JSON, String, Text, event)
from todo_backend.infrastructure.database.database import Base

logger = logging.getLogger(__name__)
class Users(Base):
    logger.info("Initializing Users model")
    __tablename__ = "users"  # Sửa ở đây

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)
    role = Column(String(50))
    phone_number = Column(String(20), nullable=True)
    

class Todo(Base):
    logger.info("Initializing Todo model")
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    description = Column(Text)
    priority = Column(Integer, default=1)
    completed = Column(Boolean, default=False)
    status = Column(String(30), default="not_started", nullable=False)
    thumbnail_url = Column(String(1024), nullable=True)
    is_vital = Column(Boolean, default=False, nullable=False)
    checklist_data = Column(JSON, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class TaskStatus(Base):
    __tablename__ = "task_statuses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    order_index = Column(Integer, default=0, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class TaskPriority(Base):
    __tablename__ = "task_priorities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    level = Column(Integer, nullable=False)
    order_index = Column(Integer, default=0, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class ChatThread(Base):
    __tablename__ = "chat_threads"

    # Giữ tương thích với thread_id dạng string hiện có
    id = Column(String(128), primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=True)
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
    thread_id = Column(String(128), ForeignKey("chat_threads.id"), nullable=False, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # user | assistant | system
    content = Column(Text, nullable=False)
    metadata_json = Column("metadata", Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


Index("ix_chat_messages_owner_thread_created", ChatMessage.owner_id, ChatMessage.thread_id, ChatMessage.created_at)


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    type = Column(String(100), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    metadata_json = Column("metadata", JSON, nullable=True)
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    read_at = Column(DateTime, nullable=True)


Index("ix_notifications_user_read_created", Notification.user_id, Notification.is_read, Notification.created_at)

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