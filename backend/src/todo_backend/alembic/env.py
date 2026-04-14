import os
import sys
from pathlib import Path

# Add backend/src into sys.path so `todo_backend` package can be imported reliably.
CURRENT_FILE = Path(__file__).resolve()
SRC_PATH = CURRENT_FILE.parents[2]
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))
from logging.config import fileConfig

from alembic import context
from todo_backend.domain.entities import models
from sqlalchemy import engine_from_config, pool

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config


def _normalize_database_url(database_url: str) -> str:
    if database_url.startswith("mssql://"):
        return database_url.replace("mssql://", "mssql+pyodbc://", 1)
    return database_url


# Prefer DATABASE_URL from environment for deployment/multi-env usage.
database_url = os.getenv("DATABASE_URL") or config.get_main_option("sqlalchemy.url")
if database_url:
    config.set_main_option("sqlalchemy.url", _normalize_database_url(database_url))

# Interpret the config file for Python logging.
# This line sets up loggers basically.

fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = models.Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        render_as_batch=url.startswith("sqlite"),
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            render_as_batch=config.get_main_option("sqlalchemy.url").startswith("sqlite"),
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
