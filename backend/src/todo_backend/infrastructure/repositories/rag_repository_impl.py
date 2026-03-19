import logging

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings

from ...domain.repositories_interface.rag_repository import RAGRepository

logger = logging.getLogger(__name__)

class ChromaRAGRepository(RAGRepository):
    
    def __init__ ( self , embedding_model: GoogleGenerativeAIEmbeddings , persist_directory: str):
        self.client = Chroma(
            collection_name="user_documents",
            embedding_function=embedding_model,
            persist_directory=persist_directory
        )
        self.embedding_model = embedding_model
        logger.info(f" CREATE CHROMA RAG FOR REPONSITORY  {persist_directory}")

    def search_documents(self, user_id : int , query : str , k: int = 3) -> list[Document]:
        logger.info(f" FIND {user_id}, WITH query IS {query} ")
        results = self.client.similarity_search(
            query=query,
            k = k ,
            filter ={"owner_id": user_id }
        )
        return results 
    
    def add_document(self, user_id: int, text: str, metadata: dict = None) -> str:
        doc_metadata = metadata or {}
        doc_metadata["owner_id"] = user_id
        
        doc = Document(page_content=text, metadata=doc_metadata)
        logger.info(f"ADD DOCUMENT FOR {user_id}")
        doc_ids = self.client.add_documents([doc])  
        doc_id = doc_ids[0] if doc_ids else "unknown"
        return f"ADD DOCUMENT SUCCESSFULLY FOR id: {doc_id}"  
    
    def get_all_documents_for_user(self, user_id: int) -> list[Document]:
        """
        Lấy TẤT CẢ các document cho một user_id cụ thể.
        Việc này cần thiết để 'fit' mô hình BM25
        """
        try:
            logger.info(f"Fetching all documents for user {user_id} for BM25 fitting...") 
            
            results = self.client.get(
                where={"owner_id": user_id},
                include=["documents", "metadatas"] 
            )
            
            if not results.get("ids"):
                logger.warning(f"No documents found for user {user_id}")
                return []

            documents = []
            for i in range(len(results["ids"])):
                documents.append(
                    Document(
                        page_content=results["documents"][i],
                        metadata=results["metadatas"][i]
                    )
                )
            
            logger.info(f"Fetched {len(documents)} documents for user {user_id}")
            return documents

        except Exception as e:
            logger.error(f"Error fetching all documents for user {user_id}: {e}")
            return []