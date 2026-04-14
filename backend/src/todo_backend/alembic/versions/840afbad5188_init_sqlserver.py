"""init_sqlserver

Revision ID: 840afbad5188
Revises: 
Create Date: 2026-03-27 15:21:10.665074

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = '840afbad5188'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    def table_exists(table_name: str) -> bool:
        return inspector.has_table(table_name)

    def index_exists(table_name: str, index_name: str) -> bool:
        existing = {idx["name"] for idx in inspector.get_indexes(table_name)}
        return index_name in existing

    if not table_exists("users"):
        op.create_table(
            "users",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("email", sa.String(length=255), nullable=False),
            sa.Column("username", sa.String(length=100), nullable=False),
            sa.Column("first_name", sa.String(length=100), nullable=True),
            sa.Column("last_name", sa.String(length=100), nullable=True),
            sa.Column("hashed_password", sa.String(length=255), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=True),
            sa.Column("role", sa.String(length=50), nullable=True),
            sa.Column("phone_number", sa.String(length=20), nullable=True),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("email"),
            sa.UniqueConstraint("username"),
        )
        inspector = inspect(bind)
    if table_exists("users") and not index_exists("users", op.f("ix_users_id")):
        op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    if not table_exists("chat_threads"):
        op.create_table(
            "chat_threads",
            sa.Column("id", sa.String(length=128), nullable=False),
            sa.Column("owner_id", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=255), nullable=True),
            sa.Column("is_deleted", sa.Boolean(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        inspector = inspect(bind)
    if table_exists("chat_threads") and not index_exists("chat_threads", op.f("ix_chat_threads_id")):
        op.create_index(op.f("ix_chat_threads_id"), "chat_threads", ["id"], unique=False)
    if table_exists("chat_threads") and not index_exists("chat_threads", op.f("ix_chat_threads_owner_id")):
        op.create_index(op.f("ix_chat_threads_owner_id"), "chat_threads", ["owner_id"], unique=False)

    if not table_exists("task_priorities"):
        op.create_table(
            "task_priorities",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=100), nullable=False),
            sa.Column("level", sa.Integer(), nullable=False),
            sa.Column("order_index", sa.Integer(), nullable=False),
            sa.Column("owner_id", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        inspector = inspect(bind)
    if table_exists("task_priorities") and not index_exists("task_priorities", op.f("ix_task_priorities_id")):
        op.create_index(op.f("ix_task_priorities_id"), "task_priorities", ["id"], unique=False)
    if table_exists("task_priorities") and not index_exists("task_priorities", op.f("ix_task_priorities_owner_id")):
        op.create_index(op.f("ix_task_priorities_owner_id"), "task_priorities", ["owner_id"], unique=False)

    if not table_exists("task_statuses"):
        op.create_table(
            "task_statuses",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=100), nullable=False),
            sa.Column("order_index", sa.Integer(), nullable=False),
            sa.Column("owner_id", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        inspector = inspect(bind)
    if table_exists("task_statuses") and not index_exists("task_statuses", op.f("ix_task_statuses_id")):
        op.create_index(op.f("ix_task_statuses_id"), "task_statuses", ["id"], unique=False)
    if table_exists("task_statuses") and not index_exists("task_statuses", op.f("ix_task_statuses_owner_id")):
        op.create_index(op.f("ix_task_statuses_owner_id"), "task_statuses", ["owner_id"], unique=False)

    if not table_exists("todos"):
        op.create_table(
            "todos",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=255), nullable=True),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("priority", sa.Integer(), nullable=True),
            sa.Column("completed", sa.Boolean(), nullable=True),
            sa.Column("status", sa.String(length=30), nullable=False),
            sa.Column("thumbnail_url", sa.String(length=1024), nullable=True),
            sa.Column("is_vital", sa.Boolean(), nullable=False),
            sa.Column("checklist_data", sa.JSON(), nullable=True),
            sa.Column("owner_id", sa.Integer(), nullable=True),
            sa.Column("due_date", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        inspector = inspect(bind)
    if table_exists("todos") and not index_exists("todos", op.f("ix_todos_id")):
        op.create_index(op.f("ix_todos_id"), "todos", ["id"], unique=False)

    if not table_exists("chat_messages"):
        op.create_table(
            "chat_messages",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("thread_id", sa.String(length=128), nullable=False),
            sa.Column("owner_id", sa.Integer(), nullable=False),
            sa.Column("role", sa.String(length=20), nullable=False),
            sa.Column("content", sa.Text(), nullable=False),
            sa.Column("metadata", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
            sa.ForeignKeyConstraint(["thread_id"], ["chat_threads.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        inspector = inspect(bind)
    if table_exists("chat_messages") and not index_exists("chat_messages", op.f("ix_chat_messages_id")):
        op.create_index(op.f("ix_chat_messages_id"), "chat_messages", ["id"], unique=False)
    if table_exists("chat_messages") and not index_exists("chat_messages", op.f("ix_chat_messages_owner_id")):
        op.create_index(op.f("ix_chat_messages_owner_id"), "chat_messages", ["owner_id"], unique=False)
    if table_exists("chat_messages") and not index_exists("chat_messages", "ix_chat_messages_owner_thread_created"):
        op.create_index(
            "ix_chat_messages_owner_thread_created",
            "chat_messages",
            ["owner_id", "thread_id", "created_at"],
            unique=False,
        )
    if table_exists("chat_messages") and not index_exists("chat_messages", op.f("ix_chat_messages_thread_id")):
        op.create_index(op.f("ix_chat_messages_thread_id"), "chat_messages", ["thread_id"], unique=False)


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_chat_messages_thread_id'), table_name='chat_messages')
    op.drop_index('ix_chat_messages_owner_thread_created', table_name='chat_messages')
    op.drop_index(op.f('ix_chat_messages_owner_id'), table_name='chat_messages')
    op.drop_index(op.f('ix_chat_messages_id'), table_name='chat_messages')
    op.drop_table('chat_messages')
    op.drop_index(op.f('ix_todos_id'), table_name='todos')
    op.drop_table('todos')
    op.drop_index(op.f('ix_task_statuses_owner_id'), table_name='task_statuses')
    op.drop_index(op.f('ix_task_statuses_id'), table_name='task_statuses')
    op.drop_table('task_statuses')
    op.drop_index(op.f('ix_task_priorities_owner_id'), table_name='task_priorities')
    op.drop_index(op.f('ix_task_priorities_id'), table_name='task_priorities')
    op.drop_table('task_priorities')
    op.drop_index(op.f('ix_chat_threads_owner_id'), table_name='chat_threads')
    op.drop_index(op.f('ix_chat_threads_id'), table_name='chat_threads')
    op.drop_table('chat_threads')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###
