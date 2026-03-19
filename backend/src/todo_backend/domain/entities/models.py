#D:\Todos\thangtm25-Todos\Todos\backend\src\todo_backend\domain\entities\models.py
import logging

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, event , DateTime
from typing import Optional
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