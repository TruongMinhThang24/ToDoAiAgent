#D:\Todos\thangtm25-Todos\Todos\backend\src\todo_backend\infrastructure\database\database.py
import logging

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from todo_backend.config.setting import settings

logger = logging.getLogger(__name__)

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

try:
    # Tạo engine kết nối
    logger.info(f"Connecting to database at {SQLALCHEMY_DATABASE_URL}")
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
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