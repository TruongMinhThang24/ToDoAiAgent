# src/todo_backend/infrastructure/agent/dependencies.py
import logging
import asyncio
from typing import Optional

from flashrank import Ranker
from langchain_google_genai import (ChatGoogleGenerativeAI,
                                    GoogleGenerativeAIEmbeddings)
from fastapi import HTTPException
from ...app.usecases.rag import RAGUseCases
from ...config.setting import settings
from ..repositories.rag_repository_impl import ChromaRAGRepository
from langchain_tavily import TavilySearch

from sqlalchemy import Table, Column, Integer, String, JSON, MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.sql import select
logger = logging.getLogger(__name__)

app_gemini_model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.85,
    google_api_key=settings.GEMINI_API_KEY
)

app_embedding_model = GoogleGenerativeAIEmbeddings(
    model = "models/text-embedding-004",
    google_api_key=settings.GEMINI_API_KEY
)


# === RAG SERVICE (Singleton) ===
chroma_path = settings.CHROMA_PERSIST_DIRECTORY

app_rag_repository = ChromaRAGRepository(
    embedding_model=app_embedding_model,
    persist_directory=chroma_path 
)

try:
    logger.info("Initializing FlashRank Reranker...")
    app_reranker = Ranker(model_name="ms-marco-MiniLM-L-12-v2") 
    logger.info("FlashRank Reranker initialized.")
except Exception as e:
    logger.error(f"Failed to initialize Reranker: {e}")
    app_reranker = None


app_rag_usecase = RAGUseCases(
    rag_repository=app_rag_repository,
    reranker=app_reranker
    )

# === TAVILY SEARCH TOOL (Singleton) - REFACTORED ===
logger.info("Initializing Tavily Search Tool...")
app_tavily_tool: TavilySearch | None = None  
if not settings.TAVILY_API_KEY:
    logger.warning("TAVILY_API_KEY not found in settings. Internet search tool will be disabled.")
else:
    try:
        app_tavily_tool = TavilySearch(
            max_results=5, 
            api_key=settings.TAVILY_API_KEY
        )
        logger.info("Tavily Search Tool initialized successfully.")
    except Exception as e:
        
        logger.error(f"Failed to initialize Tavily Search Tool: {e}", exc_info=True)
        app_tavily_tool = None
# ===================================================
# === Async Postgres-based Checkpointer ===
db_url = settings.DATABASE_URL
# Ensure async driver for SQLAlchemy
if db_url.startswith("postgresql://") or db_url.startswith("postgres://"):
    async_db_url = db_url.replace("postgres://", "postgresql+asyncpg://") if db_url.startswith("postgres://") else db_url.replace("postgresql://", "postgresql+asyncpg://")
else:
    # Fallback - treat as sqlite path or others (not ideal)
    async_db_url = db_url

metadata = MetaData()
agent_checkpoints = Table(
    "agent_checkpoints",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("thread_id", String(255), index=True),
    Column("data", JSON),
    Column("created_at", String(64))
)

class AsyncPostgresSaver:
    """A minimal async checkpointer that stores JSON checkpoints in Postgres.

    Methods: `save(thread_id, checkpoint_dict)` and `load(thread_id)` are async.
    """
    def __init__(self, engine: AsyncEngine):
        self._engine = engine

    async def init_db(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(metadata.create_all)

    async def save(self, thread_id: str, checkpoint: dict) -> None:
        async with self._engine.begin() as conn:
            await conn.execute(
                agent_checkpoints.insert().values(
                    thread_id=thread_id,
                    data=checkpoint,
                    created_at=str(__import__('datetime').datetime.utcnow())
                )
            )

    async def load(self, thread_id: str) -> Optional[dict]:
        async with self._engine.connect() as conn:
            q = select(agent_checkpoints.c.data).where(agent_checkpoints.c.thread_id == thread_id).order_by(agent_checkpoints.c.id.desc()).limit(1)
            res = await conn.execute(q)
            row = res.fetchone()
            return row[0] if row else None

    # For compatibility with some sync callers, provide synchronous wrappers
    def save_sync(self, thread_id: str, checkpoint: dict) -> None:
        asyncio.get_event_loop().run_until_complete(self.save(thread_id, checkpoint))

    def load_sync(self, thread_id: str) -> Optional[dict]:
        return asyncio.get_event_loop().run_until_complete(self.load(thread_id))


class InMemoryCheckpointer:
    """Fallback checkpointer để tránh làm hỏng toàn bộ chat khi DB async không khả dụng."""

    def __init__(self):
        self._store: dict[str, dict] = {}

    async def save(self, thread_id: str, checkpoint: dict) -> None:
        self._store[thread_id] = checkpoint

    async def load(self, thread_id: str) -> Optional[dict]:
        return self._store.get(thread_id)

    def save_sync(self, thread_id: str, checkpoint: dict) -> None:
        self._store[thread_id] = checkpoint

    def load_sync(self, thread_id: str) -> Optional[dict]:
        return self._store.get(thread_id)

try:
    async_engine = create_async_engine(async_db_url, echo=False)
    app_checkpointer = AsyncPostgresSaver(async_engine)
    # Initialize table in background
    try:
        asyncio.get_event_loop().run_until_complete(app_checkpointer.init_db())
    except Exception:
        # In some runtime contexts (tests) event loop may not be running; skip init
        pass
except Exception as e:
    logger.error(f"Failed to create async engine for checkpointer: {e}")
    app_checkpointer = InMemoryCheckpointer()
    logger.warning("Using InMemoryCheckpointer fallback.")

def get_gemini_model():
    """Dependency để cung cấp mô hình LLM."""
    return app_gemini_model

def get_embedding_model():
    """Dependency cung cấp mô hình embedding"""
    return app_embedding_model

def get_rag_usecase():
    """Dependency để cung cấp RAG Usecase."""
    return app_rag_usecase

def get_checkpointer():
    """Dependency để cung cấp bộ nhớ (memory)."""
    if app_checkpointer is None:
        logger.warning("Checkpointer unavailable; using in-memory fallback at runtime.")
        return InMemoryCheckpointer()
    return app_checkpointer
# === REFACTORED DEPENDENCY ===
def get_tavily_tool() -> TavilySearch:
    """
    Dependency to provide the Tavily Search tool.
    Raises a 503 Service Unavailable error if the tool is not configured.
    """
    if app_tavily_tool is None:
        logger.error("get_tavily_tool was called, but app_tavily_tool is None.")
        raise HTTPException(
            status_code=503, 
            detail="Internet search service is not configured or unavailable."
        )
    return app_tavily_tool


def get_optional_tavily_tool() -> TavilySearch | None:
    """Optional dependency: trả None khi Tavily chưa cấu hình, không làm fail chat endpoint."""
    if app_tavily_tool is None:
        logger.warning("Tavily tool is unavailable; continue without internet-search tool.")
        return None
    return app_tavily_tool