# Changelog

- 2026-03-20 — Task 03: Implement CSRF Protection for Cookie-based Authentication
  - Files: backend/src/main.py; backend/src/todo_backend/api/security/csrf.py; backend/src/todo_backend/api/security/__init__.py; backend/src/todo_backend/api/routers/auth.py; frontend/todo-frontend/src/lib/service/apiClient.js; docs/TESTING_GUIDE.md; docs/PROJECT_CHECKLIST.md; docs/CHANGELOG.md
  - Logic: Thêm lớp bảo vệ CSRF theo Double Submit Cookie cho request ghi dữ liệu (cookie `csrf_token` + header `X-CSRF-Token`), phát hành/xóa `csrf_token` tại login/logout, giữ auth cookie hiện tại, cập nhật Axios client tự động đính CSRF header cho `POST/PUT/PATCH/DELETE`, và hoàn tất lint/build/test.

- 2026-03-20 — Task 02: Migrate JWT from LocalStorage to HttpOnly Cookie
  - Files: backend/src/todo_backend/api/routers/auth.py; backend/src/todo_backend/api/routers/error_test.py; backend/src/todo_backend/api/routers/chat.py; backend/src/todo_backend/app/usecases/scheduler.py; frontend/todo-frontend/src/lib/service/apiClient.js; frontend/todo-frontend/src/features/auth/login/infrastructure/authRepository.js; frontend/todo-frontend/src/features/todos/components/TodoNavbar.jsx; frontend/todo-frontend/src/features/todos/components/TodoInbox.jsx; docs/PROJECT_CHECKLIST.md; docs/CHANGELOG.md
  - Logic: Chuyển cơ chế auth từ localStorage + Authorization header sang HttpOnly cookie (`set_cookie` khi login, đọc cookie trong `get_current_user`, `POST /auth/logout` xóa cookie), bật `withCredentials` ở client, xóa localStorage token flow, bổ sung logout flow frontend gọi API backend, và xử lý sạch lỗi lint/test phát sinh trong backend.

- 2026-03-20 — Checklist đánh dấu chức năng
  - Files: backend/src/todo_backend/app/usecases/agent_service.py; backend/tests/test_agent_service.py; docs/PROJECT_CHECKLIST.md; docs/CHANGELOG.md
  - Logic: Chọn invoke/ainvoke phù hợp checkpointer sync/async để tránh lỗi threading, thêm guard tool_calls, bổ sung unit tests cho hai đường gọi, cập nhật checklist và changelog sau khi test pass.
