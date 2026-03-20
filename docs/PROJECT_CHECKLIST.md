# Project Checklist

- [x] Checklist đánh dấu chức năng — cập nhật AgentService chọn invoke/ainvoke theo checkpointer sync/async, thêm guard tool_calls và bổ sung unit tests hai đường gọi (2026-03-20)
- [x] Báo cáo tài liệu — cập nhật PROJECT_CHECKLIST và CHANGELOG theo Phase 4 sau khi test pass (2026-03-20)

### Task 02: Migrate JWT from LocalStorage to HttpOnly Cookie

- [✅] Backend: cập nhật API login (`/token` hoặc `/login`) tại [backend/src/todo_backend/api/routers/auth.py](backend/src/todo_backend/api/routers/auth.py) để set cookie `access_token` với `httponly=True`, `secure=False` (dev), `samesite="lax"`, `max_age` theo TTL token.
- [✅] Backend: cập nhật dependency `get_current_user` để đọc token từ `request.cookies.get("access_token")` thay vì header `Authorization`.
- [✅] Backend: thêm API `POST /logout` tại [backend/src/todo_backend/api/routers/auth.py](backend/src/todo_backend/api/routers/auth.py), dùng `delete_cookie(key="access_token", httponly=True, samesite="lax")`.
- [✅] Frontend: xóa hoàn toàn flow token trong `localStorage` và bỏ gắn `Authorization: Bearer ...` ở interceptor.
- [✅] Frontend: thêm `withCredentials: true` trong [frontend/todo-frontend/src/lib/service/apiClient.js](frontend/todo-frontend/src/lib/service/apiClient.js).
- [✅] Frontend: cập nhật logic logout gọi API `/logout`, sau đó redirect về trang login.
- [✅] Verify Backend:
    - [✅] `poetry run ruff check src/`
    - [✅] `poetry run pytest -q`
- [✅] Verify Frontend:
    - [✅] `npm run lint`
    - [✅] `npm run build`

    
### Task 03: Implement CSRF Protection for Cookie-based Authentication

- [✅] Backend: Cập nhật login để set đồng thời `access_token` cookie và `csrf_token` cookie tại [backend/src/todo_backend/api/routers/auth.py](backend/src/todo_backend/api/routers/auth.py).
- [✅] Backend: Thiết kế CSRF validation theo Double Submit Cookie (đọc `csrf_token` từ cookie + `X-CSRF-Token` từ header, so khớp giá trị).
- [✅] Backend: Áp dụng CSRF validation cho các endpoint thay đổi dữ liệu trong nhóm router tại [backend/src/todo_backend/api/routers](backend/src/todo_backend/api/routers) (bao gồm logout, CRUD/toggle todo, update user/change-password và các endpoint ghi dữ liệu khác).
- [✅] Backend: Không áp CSRF cho GET/HEAD/OPTIONS và health check.
- [✅] Backend: Chuẩn hóa response khi CSRF thiếu/sai: HTTP 403 với message nhất quán `"CSRF token missing or invalid"`.
- [✅] Backend: Logout phải xóa cả `access_token` và `csrf_token` cookie tại [backend/src/todo_backend/api/routers/auth.py](backend/src/todo_backend/api/routers/auth.py).
- [✅] Backend: Giữ tương thích dependency xác thực hiện tại, không làm hỏng API đang dùng auth cookie.
- [✅] Frontend: Cập nhật [frontend/todo-frontend/src/lib/service/apiClient.js](frontend/todo-frontend/src/lib/service/apiClient.js):
  - [✅] Giữ `withCredentials: true`
  - [✅] Tự động đính `X-CSRF-Token` cho `POST/PUT/PATCH/DELETE` bằng giá trị `csrf_token` trong cookie.
- [✅] Frontend: Rà soát login/logout flow để bảo đảm CSRF cookie hoạt động đúng và không dùng localStorage/sessionStorage cho JWT/CSRF.
- [✅] Frontend: Xử lý lỗi 403 CSRF với thông báo rõ ràng yêu cầu refresh/re-login.
- [✅] Verify Backend:
  - [✅] `poetry run ruff check src/`
  - [✅] `poetry run pytest -q`
- [✅] Verify Frontend:
  - [✅] `npm run lint`
  - [✅] `npm run build`
- [✅] Manual E2E:
  - [✅] Login → tạo/sửa/xóa todo thành công
  - [✅] Sửa/xóa CSRF token thủ công → request ghi dữ liệu bị chặn 403
  - [✅] Logout xóa đủ 2 cookie (`access_token`, `csrf_token`)