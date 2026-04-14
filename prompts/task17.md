# 🎯 Task 17: UI/UX Refactoring & Hoàn thiện Full Tính năng Chat

## 1. Context
Tính năng BYOK đã chạy tốt ở Backend, nhưng Frontend đang gặp 3 vấn đề lớn:
1. UI/UX sai vị trí: Ô nhập API Key đang nằm chềnh ềnh trong màn hình Chat. Cần dời nó sang page `Settings`.
2. Lịch sử Chat (Sidebar) đang bị "liệt": Bấm vào không load được tin nhắn cũ, không tiếp tục được phiên chat (AI không nhớ).
3. Thiếu nút Upload File: Backend đã hỗ trợ RAG/File, nhưng UI không có nút chọn file để gửi kèm.

## 2. Requirements (Thực hiện tuần tự 3 Bước cho Frontend)

Bạn BẮT BUỘC thực hiện theo luồng sau:

**BƯỚC 1: DỜI NHÀ CHO BYOK (Settings Page)**
- Xóa toàn bộ khối UI "Your Gemini API Key" ra khỏi Component `Chat`.
- Tìm/Tạo Component `Settings` (tương ứng với menu Settings trên Sidebar trái). Dựng form nhập API Key ở đó.
- Vẫn giữ nguyên logic lưu key vào `localStorage`. Luồng gọi API Chat vẫn phải tự động lấy key từ `localStorage` để nhét vào Header.

**BƯỚC 2: TÍCH HỢP CHAT HISTORY (Tiếp tục phiên chat cũ)**
- Truy vết component Sidebar "Chat History".
- Thêm sự kiện `onClick`: Khi user bấm vào một mục lịch sử, phải gọi API (VD: `GET /api/v1/chat/threads/{thread_id}/messages`) để tải toàn bộ tin nhắn cũ.
- Cập nhật State: Đổ tin nhắn cũ ra màn hình chat. **QUAN TRỌNG NHẤT:** Gán `active_thread_id = id_vừa_chọn` để khi user gửi tin nhắn tiếp theo, API `fetch` stream sẽ gửi kèm cái `thread_id` này xuống Backend.

**BƯỚC 3: THÊM NÚT UPLOAD FILE (Luồng RAG)**
- Tại Component `Chat`, ngay cạnh ô Input "Type your message...", hãy thêm một nút Đính kèm (Paperclip icon / Upload button).
- Viết hàm xử lý `<input type="file" />` (lưu file vào State, hiện tên file preview nhỏ trên ô input).
- Sửa lại hàm Submit: Nếu có file, hãy điều chỉnh payload gửi xuống Backend cho đúng contract (thường là đổi sang `multipart/form-data` hoặc gọi API upload riêng trước rồi lấy file_url nhét vào payload chat).

HÀNH ĐỘNG CỦA BẠN BÂY GIỜ:
Đọc kỹ cấu trúc file Frontend hiện tại. Hãy nhả các Code Block (Edit Proposal) để refactor TỪNG FILE một:
1. File `Settings` (Thêm form BYOK)
2. File `Chat` (Xóa BYOK, thêm nút Upload File, tích hợp hàm onClick cho Chat History, load messages, quản lý `thread_id`).