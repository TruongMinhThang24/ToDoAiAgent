# src/todo_backend/infrastructure/agent/dependencies.py
import logging
import sqlite3

from flashrank import Ranker
from langchain_google_genai import (ChatGoogleGenerativeAI,
                                    GoogleGenerativeAIEmbeddings)
from langgraph.checkpoint.sqlite import SqliteSaver
from fastapi import HTTPException
from ...app.usecases.rag import RAGUseCases
from ...config.setting import settings
from ..repositories.rag_repository_impl import ChromaRAGRepository
from langchain_tavily import TavilySearch
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
db_path_prefix = settings.DATABASE_URL
db_path = db_path_prefix.replace("sqlite:///","")
conn = sqlite3.connect(db_path , check_same_thread=False)
app_checkpointer = SqliteSaver(conn = conn)

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