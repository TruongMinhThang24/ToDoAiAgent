import logging
import re
from typing import List

from flashrank import Ranker , RerankRequest
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rank_bm25 import BM25Okapi

from ...domain.repositories_interface.rag_repository import RAGRepository

logger = logging.getLogger(__name__)

def bm25_tokenizer(text: str) -> List[str]:
    # Đơn giản là split theo khoảng trắng, lọc ký tự và đổi sang chữ thường
    text = re.sub(r'[^\w\s]', '', text.lower())
    return text.split()

class RAGUseCases:
 
    def __init__(self, rag_repository: RAGRepository , reranker: Ranker):
        self.rag_repository = rag_repository 
        self.reranker= reranker
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=300,
      
            separators=["\n\n", "\n", ". ", " ", ""],
            keep_separator=True
        )

    def retrieve_context(self, user_id: int, query: str) -> str:
        logger.info(f"Hybrid Search starting for user {user_id} with query: '{query}'")
        K_RETRIEVE = 20 # Lấy 20 kết quả từ mỗi phương thức
        K_RERANK = 5    # Lấy 5 kết quả tốt nhất sau cùng

        try:
          
            vector_docs = self.rag_repository.search_documents(
                user_id=user_id, 
                query=query, 
                k=K_RETRIEVE
            )

            # === BƯỚC 2: KEYWORD SEARCH (BM25) ===
            # Lấy TẤT CẢ docs để fit BM25 (chỉ chạy khi cần)
            # Chúng ta dùng hàm mới thêm vào repository
            all_user_docs = self.rag_repository.get_all_documents_for_user(user_id)
            keyword_docs = []
            if all_user_docs:
                corpus = [doc.page_content for doc in all_user_docs]
                if corpus:
                    tokenized_corpus = [bm25_tokenizer(doc) for doc in corpus]
                    if tokenized_corpus:
                        bm25 = BM25Okapi(tokenized_corpus)
                        tokenized_query = bm25_tokenizer(query)
                        if tokenized_query:  # SỬA: Check rỗng
                            bm25_scores = bm25.get_scores(tokenized_query)
                            top_n_indices = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)[:K_RETRIEVE]
                            keyword_docs = [all_user_docs[i] for i in top_n_indices if bm25_scores[i] > 0]
                            logger.info(f"BM25 found {len(keyword_docs)} relevant docs.")
                    else:
                        logger.warning(f"Tokenized corpus empty for user {user_id}.")
                else:
                    logger.warning(f"No text content for user {user_id}.")
            else:
                logger.warning(f"No documents for user {user_id}.")


            # === BƯỚC 3: FUSION (Kết hợp) ===
            # Cách đơn giản là gộp 2 list và loại bỏ trùng lặp (dùng page_content làm key)
            combined_docs = {doc.page_content: doc for doc in vector_docs}
            combined_docs.update({doc.page_content: doc for doc in keyword_docs})
            
            fused_documents = list(combined_docs.values())
            logger.info(f"Hybrid Fusion: Total unique docs pre-rerank: {len(fused_documents)}")

            if not fused_documents:
                return "Không tìm thấy tài liệu nào liên quan."

            # === BƯỚC 4: RERANK (FlashRank) ===
            # Chuyển đổi sang định dạng FlashRank
            top_passages = []
            if self.reranker:
                passages = [{"id": i, "text": doc.page_content} for i, doc in enumerate(fused_documents)]
                rerank_request = RerankRequest(query=query, passages=passages)
                reranked_passages = self.reranker.rerank(rerank_request)  # Chỉ 1 arg: object
                top_passages = reranked_passages[:K_RERANK]
            else:
                # Fallback: Sort fused bằng random hoặc length
                top_passages = [{"id": i, "text": doc.page_content, "score": 1.0} for i, doc in enumerate(fused_documents[:K_RERANK])]

            if not top_passages:
                return "Không tìm thấy thông tin phù hợp sau khi lọc."

            # === BƯỚC 5: AUGMENT (Tạo Context) ===
            context_str = "Dưới đây là thông tin liên quan nhất (kết hợp keyword và semantic search):\n\n"
            for passage in top_passages:
                logger.info(f"Hybrid: Passage score {passage.get('score', 'N/A'):.4f}")
                context_str += f"---(Trích Dẫn - Độ liên quan: {passage.get('score', 1.0):.2f})---\n"
                context_str += f"{passage['text']}\n---(Hết trích dẫn)---\n\n"
            
            return context_str    
        except Exception as e:
            logger.error(f"Error during Hybrid Search: {e}", exc_info=True)
            return "Lỗi: Không thể thực hiện tìm kiếm hybrid."
        
    def add_document_to_knowledge_base(self, user_id: int, text: str) -> str:
        """Thêm tài liệu mới cho user."""

        chunks = self.text_splitter.split_text(text)

        chunk_count = 0
        for chunk in chunks:
            
            self.rag_repository.add_document(user_id=user_id, text=chunk, metadata={})
            chunk_count += 1

        logger.info(f"Added {chunk_count} chunks for user {user_id}")
        return f"Added document to {chunk_count} chunks."