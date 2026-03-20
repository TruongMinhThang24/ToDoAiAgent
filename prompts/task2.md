# 🎯 Task 02: Migrate JWT from LocalStorage to HttpOnly Cookie

## 1. Context (Bối cảnh)
Hệ thống hiện tại đang lưu trữ JWT (Access Token) ở `localStorage` (phía Frontend) và truyền qua Header `Authorization` (phía Backend). Điều này vi phạm nguyên tắc bảo mật OWASP vì dễ bị tấn công đánh cắp token qua XSS. 
Mục tiêu của task này là chuyển đổi toàn bộ cơ chế xác thực sang sử dụng **HttpOnly Cookie**.

## 2. Yêu cầu chi tiết (Requirements)

### ⚙️ Phía Backend (FastAPI)
Các file cần tập trung: `src/todo_backend/api/routers/auth.py` và nơi định nghĩa dependency lấy user (`get_current_user`).

1. **Cập nhật API Login (`/token` hoặc `/login`):**
   - Thay vì chỉ trả về JSON chứa `access_token`, API này phải sử dụng `Response.set_cookie()` để đính kèm token vào cookie.
   - Các tham số bắt buộc cho Cookie:
     - `key="access_token"`
     - `value=<giá_trị_token>`
     - `httponly=True` (Chống XSS)
     - `secure=False` (Tạm thời để False cho môi trường dev localhost, nếu có biến môi trường thì dùng `secure=settings.is_production`)
     - `samesite="lax"`
     - `max_age=<thời_gian_sống_của_token>`

2. **Cập nhật Dependency `get_current_user`:**
   - Sửa logic để đọc token từ Cookie (`request.cookies.get("access_token")`) thay vì đọc từ Header `Authorization` (OAuth2PasswordBearer).

3. **Thêm API Logout (`POST /logout`):**
   - Tạo endpoint mới để đăng xuất. Endpoint này sẽ gọi `Response.delete_cookie(key="access_token", httponly=True, samesite="lax")` và trả về message thành công.

### 🎨 Phía Frontend (Next.js)
Các file cần tập trung: `src/lib/service/apiClient.js` và hook đăng nhập (VD: `src/features/auth/login/application/useLogin.js`).

1. **Dọn dẹp LocalStorage:**
   - Xóa bỏ HOÀN TOÀN mọi dòng code có chứa `localStorage.setItem('authToken', ...)` hoặc `localStorage.getItem('authToken')`.
   - Xóa bỏ việc đính kèm header `Authorization: Bearer ...` trong các request interceptors.

2. **Cập nhật Axios Config (`apiClient.js`):**
   - Thêm thuộc tính `withCredentials: true` vào file cấu hình của Axios (hoặc fetch) để trình duyệt tự động đính kèm HttpOnly Cookie vào mỗi request gửi lên Backend.

3. **Cập nhật logic Đăng xuất:**
   - Khi user bấm Logout, gọi API `/logout` của backend để server tự động xóa cookie, sau đó redirect về trang Login.

## 3. Ràng buộc (Constraints)
- Phải giữ nguyên cấu trúc Clean Architecture của Backend.
- KHÔNG làm hỏng các API khác đang sử dụng `get_current_user` (như API Todos, Chat).
- Cần comment rõ ràng tại những vị trí sửa đổi cookie.