# 🎯 Task 07: TDD & Fix Backend Debt - Cơ chế xác thực WebSocket với HttpOnly Cookie

## 1. Context
Hiện tại API `/api/v1/notifications/ws` ở Backend đang yêu cầu token qua Header (`Authorization: Bearer <token>`). Tuy nhiên, ở Task 02, chúng ta đã chuyển sang dùng HttpOnly Cookie để bảo mật, khiến Frontend (JavaScript) không thể đọc được JWT để nhét vào Header khi mở kết nối `ws://`. Hậu quả là tính năng Notification realtime bị tê liệt.

## 2. Requirements (TDD Workflow)
Bạn BẮT BUỘC tuân thủ luồng sau:

**NHỊP 1: VIẾT E2E/INTEGRATION TEST (BUỔI THỬ THÁCH)**
- Hãy viết 1 file test (VD: `backend/tests/test_websocket_auth.py` dùng `pytest` và `TestClient` hoặc WebSockets) giả lập kịch bản: Client đăng nhập thành công (nhận HttpOnly Cookie), sau đó dùng chính Cookie đó (không dùng Header) để kết nối vào `/api/v1/notifications/ws`.
- Xuất Code Block cho file Test này. In ra câu lệnh để tôi chạy Test. CHẮC CHẮN NÓ SẼ TẠCH (vì Backend hiện tại chỉ check Header).

**NHỊP 2: CODE BACKEND BÙ LỖ VÀO (SAU KHI TÔI BÁO LỖI TEST)**
- Sau khi tôi chạy test và gửi log lỗi màu đỏ, bạn mới được phép vào file `backend/src/todo_backend/api/routers/notifications.py` (và các file dependency liên quan) để sửa logic xác thực.
- Cách giải quyết đề xuất: Cập nhật dependency của WebSocket để nó đọc `access_token` từ `websocket.cookies` (hoặc query param cấp token ngắn hạn) thay vì `websocket.headers`.
- Xuất các Code Block Backend để tôi Apply.

**NHỊP 3: VERIFY**
- Yêu cầu tôi chạy lại file Test ban nãy. Nếu xanh, chuyển sang Phase 4 (Cập nhật Changelog).

HÀNH ĐỘNG CỦA BẠN BÂY GIỜ: 
Thực hiện NHỊP 1. Nhả Code Block cho file Test WebSocket đi. TUYỆT ĐỐI không sửa code Backend lúc này!