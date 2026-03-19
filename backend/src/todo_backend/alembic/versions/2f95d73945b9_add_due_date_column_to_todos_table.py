"""Add due_date column to todos table

Revision ID: 2f95d73945b9
Revises: 
Create Date: 2025-11-07 15:13:22.756376

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2f95d73945b9'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### Sửa đổi bằng tay ###
    # Thêm cột due_date vào bảng todos
    op.add_column('todos', sa.Column('due_date', sa.DateTime(), nullable=True))
    # ### Hết phần sửa đổi ###


def downgrade() -> None:
    # ### Sửa đổi bằng tay ###
    # Xóa cột due_date khỏi bảng todos
    op.drop_column('todos', 'due_date')
    # ### Hết phần sửa đổi ###
