# 🎯 Task 03: Implement CSRF Protection for Cookie-based Authentication

## 1. Context (Bối cảnh và Lý do)

Hệ thống hiện đã chuyển sang xác thực bằng HttpOnly cookie cho JWT (`access_token`) và frontend gửi request với `withCredentials: true`. Đây là hướng bảo mật tốt hơn localStorage trước XSS, nhưng đồng thời mở ra rủi ro CSRF (Cross-Site Request Forgery) với các request thay đổi trạng thái (POST/PUT/PATCH/DELETE) nếu không có lớp bảo vệ CSRF token.

Vì vậy, cần bổ sung cơ chế CSRF protection theo mô hình cookie + header token để đảm bảo request ghi dữ liệu chỉ được thực hiện từ frontend hợp lệ của ứng dụng.

## 2. Requirements (Yêu cầu chi tiết cho Frontend và Backend)

### 2.1 Backend Requirements (FastAPI)

- Thiết kế cơ chế CSRF theo mô hình **Double Submit Cookie**:
  - Server phát hành một CSRF token (khác JWT).
  - Token được set vào cookie riêng (ví dụ: `csrf_token`, **không** cần HttpOnly để frontend đọc được).
  - Frontend phải gửi token này qua header (ví dụ: `X-CSRF-Token`) cho mọi request thay đổi dữ liệu.
  - Backend validate:
    - Cookie `csrf_token` tồn tại
    - Header `X-CSRF-Token` tồn tại
    - Hai giá trị khớp nhau
- Áp dụng validate CSRF cho toàn bộ endpoint thay đổi dữ liệu (ít nhất):
  - Auth logout
  - Todos create/update/delete/toggle
  - User update/change-password
  - Các endpoint ghi dữ liệu khác trong API
- Không yêu cầu CSRF cho các endpoint read-only (GET, HEAD, OPTIONS) và health check.
- Khi CSRF invalid/missing:
  - Trả HTTP 403
  - Message rõ ràng, nhất quán (ví dụ: `"CSRF token missing or invalid"`).
- Khi login thành công:
  - Set cả `access_token` cookie và `csrf_token` cookie.
- Khi logout:
  - Xóa cả `access_token` cookie và `csrf_token` cookie.
- Cập nhật cấu hình bảo mật cookie:
  - `SameSite=Lax` (dev), cân nhắc `Strict` tùy UX.
  - `Secure` theo môi trường (dev false, production true).
- Đảm bảo không phá vỡ dependency `get_current_user` hiện tại.

### 2.2 Frontend Requirements (Next.js + Axios)

- Cập nhật `apiClient` để:
  - Giữ `withCredentials: true`.
  - Tự động đọc `csrf_token` từ cookie và gắn vào header `X-CSRF-Token` cho các method thay đổi trạng thái (`post`, `put`, `patch`, `delete`).
- Login flow:
  - Sau login thành công, đảm bảo cookie CSRF đã tồn tại để request tiếp theo hợp lệ.
- Logout flow:
  - Gọi API logout với CSRF header đầy đủ.
- Error handling:
  - Nếu gặp 403 do CSRF, hiển thị thông báo rõ ràng và hướng dẫn user refresh/re-login.
- Không lưu JWT hoặc CSRF token vào localStorage/sessionStorage.

### 2.3 Testing Requirements

- Backend automated tests:
  - Case thiếu CSRF header → 403
  - Case thiếu CSRF cookie → 403
  - Case token mismatch → 403
  - Case hợp lệ → request thành công
- Frontend checks:
  - `npm run lint` pass
  - `npm run build` pass
- End-to-end manual checks:
  - Login -> thao tác tạo/sửa/xóa todo thành công
  - Xóa hoặc sửa CSRF token thủ công -> thao tác bị chặn 403
  - Logout xóa đủ 2 cookie

## 3. Constraints (Ràng buộc kỹ thuật)

- Tuân thủ kiến trúc hiện tại:
  - Backend theo Clean Architecture hiện có (router/usecase/repository).
  - Frontend theo cấu trúc feature-driven đang dùng.
- Không thay đổi public API response một cách breaking nếu không cần thiết.
- Không dùng giải pháp tạm thời/hardcode token.
- Không làm giảm bảo mật hiện có (không rollback về localStorage JWT).
- Code phải rõ ràng, có comment ngắn ở các đoạn security-critical.
- Hoàn tất task phải đạt:
  - Backend tests pass
  - Frontend lint + build pass
  - Tài liệu checklist/changelog được cập nhật theo workflow dự án.