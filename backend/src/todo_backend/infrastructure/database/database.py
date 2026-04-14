#D:\Todos\thangtm25-Todos\Todos\backend\src\todo_backend\infrastructure\database\database.py
import logging

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from todo_backend.config.setting import settings

logger = logging.getLogger(__name__)

def _normalize_database_url(database_url: str) -> str:
    """
    Normalize DB URL for SQLAlchemy drivers.

    - Keep SQLite URLs as-is.
    - Convert legacy `mssql://` to `mssql+pyodbc://`.
    """
    if database_url.startswith("mssql://"):
        return database_url.replace("mssql://", "mssql+pyodbc://", 1)
    return database_url


SQLALCHEMY_DATABASE_URL = _normalize_database_url(settings.DATABASE_URL)


def _build_engine(database_url: str):
    """
    Build SQLAlchemy engine by dialect.

    - SQLite requires `check_same_thread=False` for local dev usage.
    - SQL Server / other server DBs should not receive sqlite-only args.
    """
    engine_kwargs = {}
    if database_url.startswith("sqlite"):
        engine_kwargs["connect_args"] = {"check_same_thread": False}
    else:
        engine_kwargs["pool_pre_ping"] = True

    return create_engine(database_url, **engine_kwargs)

try:
    # Tạo engine kết nối
    logger.info(f"Connecting to database at {SQLALCHEMY_DATABASE_URL}")
    engine = _build_engine(SQLALCHEMY_DATABASE_URL)
    logger.info("Database engine created successfully")
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    raise

# Tạo session
try:
    sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("Session maker initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize session maker: {e}")
    raise

# Base class cho các model
try:
    Base = declarative_base()
    logger.info("Declarative base initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize declarative base: {e}")
    raise


def ensure_todos_schema_compatibility() -> None:
    """
    Runtime safety migration for local SQLite DB.

    Context:
    - Existing developers may have an older `todos` table created before new columns
      (`status`, `thumbnail_url`, `is_vital`, `checklist_data`, `due_date`, `created_at`).
    - SQLite `create_all()` does not alter existing tables, so inserts may fail with:
      "table todos has no column named is_vital".

    This helper checks current columns and adds missing ones using ALTER TABLE.
    """
    try:
        if engine.dialect.name != "sqlite":
            return

        with engine.begin() as connection:
            table_exists = connection.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name='todos'")
            ).fetchone()

            if not table_exists:
                return

            columns = connection.execute(text("PRAGMA table_info(todos)")).fetchall()
            existing_columns = {row[1] for row in columns}

            ddl_by_column = {
                "status": "ALTER TABLE todos ADD COLUMN status VARCHAR NOT NULL DEFAULT 'not_started'",
                "thumbnail_url": "ALTER TABLE todos ADD COLUMN thumbnail_url VARCHAR",
                "is_vital": "ALTER TABLE todos ADD COLUMN is_vital BOOLEAN NOT NULL DEFAULT 0",
                "checklist_data": "ALTER TABLE todos ADD COLUMN checklist_data JSON",
                "due_date": "ALTER TABLE todos ADD COLUMN due_date DATETIME",
                "created_at": "ALTER TABLE todos ADD COLUMN created_at DATETIME",
            }

            for column_name, ddl in ddl_by_column.items():
                if column_name not in existing_columns:
                    logger.warning(
                        "Detected legacy todos schema. Adding missing column '%s'",
                        column_name,
                    )
                    connection.execute(text(ddl))

            # Backfill legacy rows so runtime response validation does not fail.
            connection.execute(
                text(
                    """
                    UPDATE todos
                    SET status = CASE WHEN completed = 1 THEN 'completed' ELSE 'not_started' END
                    WHERE status IS NULL OR TRIM(status) = ''
                    """
                )
            )
            connection.execute(
                text("UPDATE todos SET is_vital = 0 WHERE is_vital IS NULL")
            )
            connection.execute(
                text("UPDATE todos SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
            )

    except Exception as exc:
        logger.error("Failed to ensure todos schema compatibility: %s", exc)
        raise