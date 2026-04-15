import logging
from typing import Optional

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings

from ...domain.repositories_interface.rag_repository import RAGRepository

logger = logging.getLogger(__name__)

class ChromaRAGRepository(RAGRepository):
    EMBEDDING_MODEL_CANDIDATES = [
        "models/embedding-001",
        "embedding-001",
        "models/text-embedding-004",
        "text-embedding-004",
        "models/gemini-embedding-001",
        "gemini-embedding-001",
    ]
    
    def __init__(
        self,
        persist_directory: str,
        embedding_model: Optional[GoogleGenerativeAIEmbeddings] = None,
        default_api_key: Optional[str] = None,
    ):
        self.persist_directory = persist_directory
        self.default_api_key = (default_api_key or "").strip() or None
        self._embedding_model_cache: dict[str, GoogleGenerativeAIEmbeddings] = {}
        self._client_cache: dict[str, Chroma] = {}
        self._selected_model_by_key: dict[str, str] = {}

        self.embedding_model = embedding_model
        self.client: Optional[Chroma] = None
        if self.embedding_model is not None:
            self.client = Chroma(
                collection_name="user_documents",
                embedding_function=self.embedding_model,
                persist_directory=persist_directory,
            )
        logger.info(f" CREATE CHROMA RAG FOR REPONSITORY  {persist_directory}")

    def _build_embedding_model(self, api_key: Optional[str] = None) -> GoogleGenerativeAIEmbeddings:
        resolved_key = (api_key or self.default_api_key or "").strip()
        key_cache_id = resolved_key or "__env_default__"

        cached_model_name = self._selected_model_by_key.get(key_cache_id)
        if cached_model_name:
            kwargs = {"model": cached_model_name}
            if resolved_key:
                kwargs["google_api_key"] = resolved_key
            return GoogleGenerativeAIEmbeddings(**kwargs)

        last_error: Exception | None = None
        for model_name in self.EMBEDDING_MODEL_CANDIDATES:
            try:
                kwargs = {"model": model_name}
                if resolved_key:
                    kwargs["google_api_key"] = resolved_key

                embedding_model = GoogleGenerativeAIEmbeddings(**kwargs)
                # Probe once to ensure model is actually available for this key/session.
                embedding_model.embed_query("healthcheck")
                self._selected_model_by_key[key_cache_id] = model_name
                logger.info("Selected embedding model '%s' for current key context.", model_name)
                return embedding_model
            except Exception as exc:
                last_error = exc
                logger.warning("Embedding model '%s' unavailable. Trying next fallback.", model_name)

        if last_error:
            raise last_error
        raise RuntimeError("No available embedding model candidates could be selected.")

    def _get_client(self, custom_api_key: Optional[str] = None) -> Chroma:
        cleaned_key = (custom_api_key or "").strip()
        if not cleaned_key or cleaned_key == self.default_api_key:
            if self.client is None:
                self.embedding_model = self._build_embedding_model(self.default_api_key)
                self.client = Chroma(
                    collection_name="user_documents",
                    embedding_function=self.embedding_model,
                    persist_directory=self.persist_directory,
                )
            return self.client

        if cleaned_key not in self._client_cache:
            embedding_model = self._embedding_model_cache.get(cleaned_key)
            if embedding_model is None:
                embedding_model = self._build_embedding_model(cleaned_key)
                self._embedding_model_cache[cleaned_key] = embedding_model

            self._client_cache[cleaned_key] = Chroma(
                collection_name="user_documents",
                embedding_function=embedding_model,
                persist_directory=self.persist_directory,
            )

        return self._client_cache[cleaned_key]

    def search_documents(
        self,
        user_id: int,
        query: str,
        k: int = 3,
        custom_api_key: Optional[str] = None,
    ) -> list[Document]:
        logger.info(f" FIND {user_id}, WITH query IS {query} ")
        results = self._get_client(custom_api_key=custom_api_key).similarity_search(
            query=query,
            k = k ,
            filter ={"owner_id": user_id }
        )
        return results 
    
    def add_document(
        self,
        user_id: int,
        text: str,
        metadata: dict = None,
        custom_api_key: Optional[str] = None,
    ) -> str:
        doc_metadata = metadata or {}
        doc_metadata["owner_id"] = user_id
        
        doc = Document(page_content=text, metadata=doc_metadata)
        logger.info(f"ADD DOCUMENT FOR {user_id}")
        doc_ids = self._get_client(custom_api_key=custom_api_key).add_documents([doc])
        doc_id = doc_ids[0] if doc_ids else "unknown"
        return f"ADD DOCUMENT SUCCESSFULLY FOR id: {doc_id}"  
    
    def get_all_documents_for_user(self, user_id: int, custom_api_key: Optional[str] = None) -> list[Document]:
        """
        Lấy TẤT CẢ các document cho một user_id cụ thể.
        Việc này cần thiết để 'fit' mô hình BM25
        """
        try:
            logger.info(f"Fetching all documents for user {user_id} for BM25 fitting...") 
            
            results = self._get_client(custom_api_key=custom_api_key).get(
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