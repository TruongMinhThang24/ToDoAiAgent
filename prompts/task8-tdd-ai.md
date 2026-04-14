# 🎯 Task 8: Deep Trace, TDD & Optimize - Tính năng Chat AI

## 1. Context
Tính năng "Chat with AI" đang hoạt động không như mong đợi. Các vấn đề tình nghi bao gồm: AI không nhớ ngữ cảnh (lỗi Memory/DB), không stream được text (lỗi SSE/WebSocket), hoặc handle lỗi timeout kém. Cần một quy trình Automation Test để bắt bệnh chính xác.

## 2. Requirements (TDD Workflow)

**NHỊP 1: TRUY VẾT & PHÂN TÍCH (Làm ngay bây giờ)**
Bạn là Senior AI Architect, hãy quét kiến trúc hiện tại:
- **Database:** Rà soát bảng `chat_threads` và `chat_messages`. Chắc chắn rằng mỗi lần chat, Backend có lưu lại lịch sử người dùng và AI.
- **LLM Engine:** Tìm file gọi LangChain/Gemini. Nó đang cấu hình `streaming=True` hay `False`? Có dùng `ConversationBufferMemory` hoặc nhồi `chat_history` vào prompt chưa?
- **API Router:** Kiểm tra endpoint chat (ví dụ `/api/v1/chat/`). Nó dùng `StreamingResponse` (REST) hay `WebSocket`?
- **Frontend:** Luồng nhận data có dùng trình đọc Stream (ví dụ: `getReader()` của Fetch API) để gõ từng chữ ra UI không?

**NHỊP 2: VIẾT TEST SCRIPT TỰ ĐỘNG (BUỔI THỬ THÁCH)**
- Viết 1 file test: `backend/tests/test_chat_ai.py`.
- **Kịch bản test khắt khe:**
  1. Tạo User -> Tạo 1 `thread_id` mới.
  2. Gửi tin nhắn 1: "Tên tôi là [Tên Random]". Kỳ vọng status 200.
  3. Gửi tin nhắn 2 vào đúng `thread_id` đó: "Tôi tên là gì?". 
  4. Assert response của tin nhắn 2 PHẢI chứa cái [Tên Random] kia (để test tính năng Memory lưu trong DB).
- Xuất Code Block cho file Test này.

**NHỊP 3: FIX BUG VÀ TỐI ƯU (Sau khi tôi báo lỗi Test)**
Dựa vào lỗi tôi gửi, bạn tiến hành sửa code Fullstack:
- Fix lỗi mất trí nhớ (Lưu/đọc DB chuẩn xác).
- Đảm bảo Backend trả về `StreamingResponse`.
- Frontend bắt lỗi thanh lịch (không crash trắng trang nếu API timeout).