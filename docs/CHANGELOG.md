# Changelog

- 2026-04-14 — Task 17: UI/UX Refactoring & Hoàn thiện Full Tính năng Chat
  - Files: frontend/todo-frontend/src/app/chat/page.jsx; frontend/todo-frontend/src/app/settings/page.jsx; frontend/todo-frontend/src/components/layout/MainShell.jsx; backend/tests/e2e_task17_chat_history_upload.py; docs/PROJECT_CHECKLIST.md; docs/TESTING_GUIDE.md; docs/CHANGELOG.md
  - Logic: Dời UI BYOK từ Chat sang Settings page (vẫn lưu `localStorage`), giữ luồng chat tự gắn `X-Gemini-API-Key`; tích hợp Chat History thật bằng API threads/messages và đồng bộ `thread_id` active khi chọn lịch sử; bổ sung nút đính kèm file trên Chat, preview file, và submit flow upload qua `/api/v1/chat/knowledge/upload` trước khi stream chat. Verify pass với `npm run lint` và `npm run build`.

- 2026-04-14 — Task 15: Implement BYOK (Gemini API Key động từ UI)
  - Files: backend/src/todo_backend/api/routers/chat.py; backend/src/todo_backend/api/routers/agent.py; backend/src/todo_backend/app/usecases/agent_service.py; backend/tests/test_chat_ai.py; frontend/todo-frontend/src/app/chat/page.jsx; docs/PROJECT_CHECKLIST.md; docs/TESTING_GUIDE.md; docs/CHANGELOG.md
  - Logic: Bổ sung luồng BYOK end-to-end với header `X-Gemini-API-Key` cho các endpoint AI; truyền `custom_api_key` từ router xuống `AgentService`; tạo/reuse agent executor theo key runtime và fallback về key mặc định từ env khi không truyền custom key; thêm UI Save/Clear key trên màn chat, lưu key vào `localStorage`, và tự động đính header vào request stream chat. Verify pass với `poetry run pytest -q tests/test_chat_ai.py`, `npm run lint`, `npm run build`.

- 2026-04-14 — Task 14: Fix LangGraph Async Checkpointer Error (SQL Server migration context)
  - Files: backend/src/todo_backend/infrastructure/agent/dependencies.py; docs/PROJECT_CHECKLIST.md; docs/CHANGELOG.md
  - Logic: Loại bỏ fallback custom `InMemoryCheckpointer` (không tương thích API mới của LangGraph, gây lỗi `get_next_version`) và thay bằng `MemorySaver` chuẩn (`from langgraph.checkpoint.memory import MemorySaver`) trong nhánh fallback khi async DB checkpointer không khả dụng với `pyodbc`; đồng thời cập nhật `get_checkpointer()` để fallback runtime cũng trả `MemorySaver()`.

- 2026-04-14 — Task 08: Deep Trace, TDD & Optimize (Chat AI memory + streaming)
  - Files: backend/tests/test_chat_ai.py; backend/tests/e2e_task08_chat_ai_stream.py; backend/src/todo_backend/infrastructure/repositories/chat_repository_impl.py; frontend/todo-frontend/src/app/chat/page.jsx; docs/TESTING_GUIDE.md; docs/PROJECT_CHECKLIST.md; docs/CHANGELOG.md
  - Logic: Thực hiện trace đầy đủ DB/LLM/API/Frontend cho luồng Chat AI; bổ sung TDD test memory theo cùng `thread_id` (`test_chat_ai.py`); sửa lỗi tương thích SQL Server ở filter boolean `is_deleted`; hoàn thiện luồng chat stream text SSE ở frontend với `getReader()` và timeout/error fallback thân thiện; thêm Playwright E2E (`e2e_task08_chat_ai_stream.py`) theo chuẩn bypass UI login bằng API + cookie injection. Kết quả verify: `poetry run pytest -q tests/test_chat_ai.py` pass, `npm run lint` pass, `poetry run python tests/e2e_task08_chat_ai_stream.py` pass.

- 2026-04-14 — Task 08 Hotfix: giảm lỗi trả lời fallback khi chat trực tiếp trên UI
  - Files: backend/src/todo_backend/app/usecases/agent_service.py; docs/PROJECT_CHECKLIST.md; docs/CHANGELOG.md
  - Logic: Bổ sung fast-path cho lời chào ngắn (`hi/hello/helo/...`) để phản hồi ổn định không phụ thuộc network/LLM; thêm retry 1 lần cho `invoke/ainvoke` trong `AgentService.run_text_command()` khi lỗi tạm thời từ provider/network, và chuẩn hóa thông báo fallback thân thiện khi hết retry.

- 2026-03-27 — Task 10: Deep Trace & Fix Silent Bugs (Change Password vertical slice)
  - Files: backend/tests/test_change_password.py; backend/src/todo_backend/api/schemas/user_schema.py; backend/src/todo_backend/app/usecases/user.py; frontend/todo-frontend/src/app/profile/page.jsx; frontend/todo-frontend/src/features/user/components/ChangePasswordForm.jsx; docs/PROJECT_CHECKLIST.md; docs/CHANGELOG.md
  - Logic: Thêm TDD test cho luồng đổi mật khẩu end-to-end theo payload từ frontend (`currentPassword/newPassword`), sửa schema backend để nhận cả camelCase/snake_case, thay submit giả ở frontend bằng gọi API thật + trạng thái loading/error/success, và sửa `UserUseCases.change_password()` dùng `CryptContext` tương thích Argon2+bcrypt để tránh lỗi `UnknownHashError`; verify pass với `python -m pytest -q tests/test_change_password.py`.

- 2026-03-27 — Task 07 (WS Auth Debt): TDD + Fix xác thực WebSocket với HttpOnly cookie
  - Files: backend/tests/test_websocket_auth.py; backend/src/todo_backend/api/routers/notifications.py; docs/PROJECT_CHECKLIST.md; docs/CHANGELOG.md
  - Logic: Viết integration test tái hiện lỗi WS auth khi client chỉ có cookie `access_token` (không gửi `Authorization`), xác nhận test đỏ (`code=1008 Missing token`), sau đó sửa endpoint websocket để ưu tiên đọc token từ `websocket.cookies['access_token']` và fallback sang `Authorization: Bearer` để giữ tương thích ngược; verify lại `poetry run pytest -q tests/test_websocket_auth.py` pass.

- 2026-03-24 — Task 05: Structured Chat History + Thread Persistence
  - Files: backend/src/todo_backend/domain/entities/models.py; backend/src/todo_backend/domain/repositories_interface/chat_repository.py; backend/src/todo_backend/infrastructure/repositories/chat_repository_impl.py; backend/src/todo_backend/app/usecases/chat_thread_service.py; backend/src/todo_backend/api/schemas/chat_schema.py; backend/src/todo_backend/api/routers/chat.py; frontend/todo-frontend/src/features/chat/infrastructure/chatRepository.js; frontend/todo-frontend/src/features/chat/application/useChat.jsx; frontend/todo-frontend/src/features/chat/components/Sidebar.jsx; frontend/todo-frontend/src/app/chat/page.jsx; backend/tests/e2e_task05_chat_threads.py; docs/TESTING_GUIDE.md; docs/PROJECT_CHECKLIST.md.
  - Logic: Bổ sung persistence cho chat threads/messages (kèm index), thêm API thread list/create/delete và message history phân trang, lưu message user/assistant từ endpoint chat, giữ tương thích endpoint lịch sử cũ, đồng bộ FE state theo `thread_id` với localStorage restore sau reload, bổ sung UI quản lý thread (new/switch/delete), và thêm Playwright E2E cho luồng create → chat → reload → restore → delete.

- 2026-03-23 — Task 04: Lọc + Sắp xếp + Tìm kiếm Todo trên màn hình danh sách
  - Files: backend/src/todo_backend/api/routers/todos.py; backend/src/todo_backend/api/schemas/todos_schema.py; backend/src/todo_backend/app/usecases/todos.py; frontend/todo-frontend/src/features/todos/infrastructure/todoRepository.js; frontend/todo-frontend/src/features/todos/application/useTodos.js; frontend/todo-frontend/src/features/todos/components/TodoInbox.jsx; frontend/todo-frontend/src/app/todos/page.jsx; docs/TESTING_GUIDE.md; docs/PROJECT_CHECKLIST.md; docs/CHANGELOG.md
  - Logic: Bổ sung truy vấn danh sách todo end-to-end gồm search theo title/description, filter theo status/view, sort theo created_at/due_date/priority, pagination và metadata response (`items`, `total`, `page`, `page_size`); đồng bộ state filter/sort với URL, debounce tìm kiếm, reset filter và empty-state action; sửa lỗi Next.js prerender cho `/todos` bằng `Suspense` boundary cho `useSearchParams`; verify pass với `poetry run pytest -q` và `npm run build`.

- 2026-03-20 — Task 03: Implement CSRF Protection for Cookie-based Authentication
  - Files: backend/src/main.py; backend/src/todo_backend/api/security/csrf.py; backend/src/todo_backend/api/security/__init__.py; backend/src/todo_backend/api/routers/auth.py; frontend/todo-frontend/src/lib/service/apiClient.js; docs/TESTING_GUIDE.md; docs/PROJECT_CHECKLIST.md; docs/CHANGELOG.md
  - Logic: Thêm lớp bảo vệ CSRF theo Double Submit Cookie cho request ghi dữ liệu (cookie `csrf_token` + header `X-CSRF-Token`), phát hành/xóa `csrf_token` tại login/logout, giữ auth cookie hiện tại, cập nhật Axios client tự động đính CSRF header cho `POST/PUT/PATCH/DELETE`, và hoàn tất lint/build/test.

- 2026-03-20 — Task 02: Migrate JWT from LocalStorage to HttpOnly Cookie
  - Files: backend/src/todo_backend/api/routers/auth.py; backend/src/todo_backend/api/routers/error_test.py; backend/src/todo_backend/api/routers/chat.py; backend/src/todo_backend/app/usecases/scheduler.py; frontend/todo-frontend/src/lib/service/apiClient.js; frontend/todo-frontend/src/features/auth/login/infrastructure/authRepository.js; frontend/todo-frontend/src/features/todos/components/TodoNavbar.jsx; frontend/todo-frontend/src/features/todos/components/TodoInbox.jsx; docs/PROJECT_CHECKLIST.md; docs/CHANGELOG.md
  - Logic: Chuyển cơ chế auth từ localStorage + Authorization header sang HttpOnly cookie (`set_cookie` khi login, đọc cookie trong `get_current_user`, `POST /auth/logout` xóa cookie), bật `withCredentials` ở client, xóa localStorage token flow, bổ sung logout flow frontend gọi API backend, và xử lý sạch lỗi lint/test phát sinh trong backend.

- 2026-03-20 — Checklist đánh dấu chức năng
  - Files: backend/src/todo_backend/app/usecases/agent_service.py; backend/tests/test_agent_service.py; docs/PROJECT_CHECKLIST.md; docs/CHANGELOG.md
  - Logic: Chọn invoke/ainvoke phù hợp checkpointer sync/async để tránh lỗi threading, thêm guard tool_calls, bổ sung unit tests cho hai đường gọi, cập nhật checklist và changelog sau khi test pass.
