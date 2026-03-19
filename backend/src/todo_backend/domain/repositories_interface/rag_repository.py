# File: backend/src/todo_backend/domain/repositories_interface/rag_repository.py
from abc import ABC, abstractmethod
from typing import List

# SỬA LỖI: Import 'Document' (số ít) mà bạn đã quên
from langchain_core.documents import Document


# SỬA LỖI: "Reponsitory" -> "Repository" (bỏ chữ 'n')
class RAGRepository(ABC):
    
    @abstractmethod
    # SỬA LỖI: "search_document" -> "search_documents" (số nhiều)
    # SỬA LỖI: "Documents" -> "Document" (số ít)
    def search_documents(self, user_id: int, query: str, k: int = 3) -> List[Document]:
        """Tìm kiếm các tài liệu liên quan cho user."""
        pass
    
    @abstractmethod
    def add_document(self, user_id: int, text: str, metadata: dict) -> str:
        """Thêm một tài liệu mới vào vector store cho user."""
        pass