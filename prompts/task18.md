# 🎯 Task 18: Fix RAG / File Upload (Lỗi 404 Embedding Model & BYOK cho Upload)

## 1. Context
Tính năng Chat đã hoạt động mượt mà với BYOK. Tuy nhiên, khi upload file đính kèm, backend bị crash với lỗi: `404 models/text-embedding-004 is not found...`.
Nguyên nhân 1: Model embedding hiện tại bị lỗi/không tồn tại, cần đổi sang bản ổn định là `models/embedding-001`.
Nguyên nhân 2: API upload file (`/api/v1/chat/knowledge/upload`) chưa bắt Header `X-Gemini-API-Key` như luồng Chat, dẫn đến việc Embedding xài key mặc định hoặc lỗi xác thực.

## 2. Requirements

**BƯỚC 1: ĐỔI TÊN MODEL EMBEDDING & TÍCH HỢP BYOK**
- Truy vết file khởi tạo Vector DB / RAG (VD: `rag_repository_impl.py`, `dependencies.py`, hoặc UseCase liên quan).
- Sửa lại hàm khởi tạo `GoogleGenerativeAIEmbeddings`: 
  1. Đổi `model="models/embedding-001"`.
  2. Phải cho phép nhận `custom_api_key` truyền vào (giống như Chat Agent). Khởi tạo với key của user, nếu không có thì fallback về biến môi trường.

**BƯỚC 2: ĐỒNG BỘ ROUTER BACKEND**
- Cập nhật Router xử lý API tải file (VD: `api/routers/chat.py` endpoint `upload`).
- Bổ sung bắt `Header` chứa API key (ví dụ `x-gemini-api-key`). Truyền key này xuống tận Repository để khởi tạo lại Embedding model cho đúng phiên đó.

**BƯỚC 3: ĐỒNG BỘ LUỒNG FRONTEND**
- Cập nhật hàm gọi API upload file ở Frontend.
- Lấy API Key từ `localStorage` và nhét vào `Headers` của request (y hệt như đã làm với luồng chat stream).

HÀNH ĐỘNG CỦA BẠN:
Nhả Code Block sửa các file Backend (Router, RAG Service/Repository) và Frontend (API Client) để giải quyết dứt điểm lỗi 404 và đồng bộ BYOK cho luồng file.