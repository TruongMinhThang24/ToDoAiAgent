#D:\Todos\thangtm25-Todos\Todos\backend\src\todo_backend\config\setting.py
import logging

from pydantic_settings import BaseSettings
from dotenv import load_dotenv 
load_dotenv()
class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    DATABASE_URL: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    GEMINI_API_KEY: str | None = None
    CHROMA_PERSIST_DIRECTORY: str
    TAVILY_API_KEY: str | None = None

    #setting langsmith 
    LANGCHAIN_TRACING_V2: str = "true"
    LANGCHAIN_ENDPOINT: str = "httpsa://api.smith.langchain.com"
    LANGCHAIN_API_KEY: str |None = None
    LANGCHAIN_PROJECT: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


logging.basicConfig(
    level=logging.INFO,  # Mức độ logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("todos.log" , encoding='utf-8'),  # Ghi log vào file
        logging.StreamHandler()           # Hiển thị log trên console
    ]
)

# Hàm tiện ích để lấy logger
def get_logger(name):
    return logging.getLogger(name)

settings = Settings()