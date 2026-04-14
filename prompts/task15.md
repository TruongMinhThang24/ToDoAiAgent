# 🎯 Task 15: Implement "Bring Your Own Key" (BYOK) - Cấu hình API Key động từ UI

## 1. Context
Hiện tại hệ thống đang bị giới hạn Quota do dùng chung 1 `GEMINI_API_KEY` fix cứng trong file `.env` ở Backend. Khi deploy, nhiều người dùng chung sẽ làm sập hệ thống (Lỗi 429 Resource Exhausted).
Cần nâng cấp kiến trúc Fullstack để cho phép người dùng tự nhập Gemini API Key của họ trên giao diện (Frontend) và Backend sẽ ưu tiên sử dụng Key này cho luồng Chat AI.

## 2. Requirements (TDD Workflow & Fullstack Implementation)

Bạn BẮT BUỘC thực hiện theo luồng sau:

**BƯỚC 1: TRUY VẾT KIẾN TRÚC HIỆN TẠI**
- Đọc code Frontend: Tìm Component giao diện phù hợp để đặt ô input (ví dụ: `Settings` page hoặc ngay trên Header của giao diện `Chat`). Tìm luồng `fetch` gọi API `/api/v1/chat/stream`.
- Đọc code Backend: Tìm Router `/api/v1/chat/...` và truy vết xuống class khởi tạo LLM Model (LangChain `ChatGoogleGenerativeAI` hoặc `GeminiClient`).

**BƯỚC 2: TIẾN HÀNH CODE BACKEND (API & Service)**
- Sửa Router `/api/v1/chat/stream` (và các endpoint AI khác): Thêm tham số bắt Header `X-Gemini-API-Key` (hoặc tên tương tự) sử dụng `FastAPI Header(None)`.
- Sửa Service/Agent: Truyền cái `custom_api_key` này xuyên suốt luồng khởi tạo LangGraph/LangChain.
- Logic khởi tạo Model: `api_key_to_use = custom_api_key or os.getenv("GEMINI_API_KEY")`. Đảm bảo luồng Async không bị ảnh hưởng.

**BƯỚC 3: TIẾN HÀNH CODE FRONTEND (UI & Storage)**
- UI: Thêm 1 Input Field (có nút Save/Clear) để người dùng nhập "Your Gemini API Key".
- Storage: Lưu key này vào `localStorage` trên trình duyệt.
- API Client: Trong hàm gọi API chat, đọc key từ `localStorage`. Nếu có, hãy nhét nó vào Headers của request `fetch`: `{"X-Gemini-API-Key": apiKey}`.

**BƯỚC 4: VERIFY (NHỊP KIỂM TRA)**
- Yêu cầu tôi khởi động lại Frontend và Backend.
- Hướng dẫn tôi nhập 1 cái key rác (ví dụ: `12345`) vào UI và chat. Kỳ vọng: Backend báo lỗi API Key không hợp lệ (như vậy là luồng đã ăn).
- Hướng dẫn tôi nhập key thật và chat. Kỳ vọng: AI trả lời mượt mà.

HÀNH ĐỘNG CỦA BẠN BÂY GIỜ:
- Phân tích kiến trúc tại Bước 1.
- Ngay lập tức nhả Code Block cho các file Backend (Router + Agent Service) theo yêu cầu Bước 2.
- Sau đó nhả Code Block cho Frontend (UI + API Client) theo yêu cầu Bước 3.