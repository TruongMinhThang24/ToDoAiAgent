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

  
### Task 04: Lọc + Sắp xếp + Tìm kiếm Todo trên màn hình danh sách
- [✅] Rà soát luồng list todos hiện tại và chốt API contract query params: `q`, `status`, `view`, `sort_by`, `sort_order`, `page`, `page_size`.
- [✅] Backend: mở rộng endpoint list todos (router todos hiện hữu) để nhận/validate enum + default + giới hạn `page_size`.
- [✅] Backend: cập nhật business logic tại `backend/src/todo_backend/app/usecases/todos.py` để hỗ trợ search (không phân biệt hoa thường), filter kết hợp, sort ổn định, overdue đúng điều kiện.
- [✅] Backend: chuẩn hóa response metadata danh sách: `items`, `total`, `page`, `page_size` (giữ tương thích tối đa với client cũ).
- [✅] Frontend: cập nhật query state + URL sync tại màn hình danh sách `frontend/todo-frontend/src/features/todos/components/TodoInbox.jsx`.
- [✅] Frontend: thêm UI tìm kiếm, filter, sort, reset; hỗ trợ empty state + CTA “Xóa bộ lọc”.
- [✅] Frontend: cập nhật gọi API tại `frontend/todo-frontend/src/features/todos/infrastructure/todoRepository.js` để truyền đầy đủ query params.
- [✅] Frontend: thêm debounce tìm kiếm 300–500ms và reset `page=1` khi đổi search/filter/sort.
- [✅] Viết test tối thiểu:
  - Backend: tổ hợp filter/search/sort.
  - Frontend: query state, mapping params, empty state.
- [✅] Lệnh verify dự kiến:
  - Backend: `cd backend && poetry run pytest -q`
  - Frontend lint/build: `cd frontend/todo-frontend && npm run lint && npm run build`

  # ...existing code...

### Task 05: Implement Structured Chat History + Thread Persistence (FE/BE)

- [x] Backend: thiết kế model/bảng lưu `thread` và `message` với các trường `thread_id`, `user_id`, `role`, `content`, `metadata`, `created_at`.
- [x] Backend: thêm index phục vụ truy vấn theo `(user_id, thread_id, created_at)` và hỗ trợ phân trang ổn định.
- [x] Backend: triển khai usecase/repository cho:
  - [x] `GET /chat/threads` (list threads theo user, có phân trang)
  - [x] `POST /chat/threads` (tạo thread mới)
  - [x] `GET /chat/threads/{thread_id}/messages` (lịch sử theo thời gian, có phân trang/cursor)
  - [x] `DELETE /chat/threads/{thread_id}` (xóa/soft-delete thread)
- [x] Backend: cập nhật endpoint chat hiện tại để:
  - [x] nhận `thread_id` từ client
  - [x] tự tạo thread nếu thiếu `thread_id`
  - [x] append message đúng thread
  - [x] trả về `thread_id` nhất quán cho FE
- [x] Backend: security & reliability:
  - [x] chỉ owner mới truy cập được thread/messages
  - [x] validate input + giới hạn độ dài message + sanitize text cơ bản
  - [x] xử lý rõ ràng khi thread không tồn tại/không thuộc user
- [x] Frontend: refactor chat state (`useChat`) để quản lý `currentThreadId`, thread list, message map theo thread.
- [x] Frontend: persist `currentThreadId` (URL query hoặc localStorage) để reload không mất ngữ cảnh.
- [x] Frontend: thêm UI thread list (sidebar/panel): hiển thị preview, thời gian cập nhật, tạo mới/chuyển/xóa thread.
- [x] Frontend: khi chọn thread phải load history và render đúng thứ tự; có loading skeleton + empty state + error state.
- [x] Frontend: gửi tin nhắn luôn kèm `thread_id`; hỗ trợ optimistic update và rollback khi request lỗi.
- [x] Frontend: UX polish tối thiểu: auto-scroll, disable input khi đang gửi, thông báo lỗi thân thiện.
- [ ] Verify backend: `cd backend && poetry run pytest -q`.
- [x] Verify frontend: `cd frontend/todo-frontend && npm run lint && npm run build`.
- [x] E2E bắt buộc: viết Playwright Python test cho flow tạo thread → chat → reload → khôi phục → xóa thread.

### Task 06: Debug & Fix luồng kết nối API (Frontend - Backend) cho Add Task

- [ ] Frontend: rà soát luồng submit Add Task từ UI handler đến repository/service gọi API.
- [ ] Frontend: kiểm tra cấu hình API client (`baseURL`, `withCredentials`, `Content-Type`, `X-CSRF-Token`) và đồng bộ endpoint backend.
- [ ] Backend: kiểm tra router tạo todo (`POST /api/v1/todos/`), CORS và chuẩn payload với schema.
- [ ] Backend: chuẩn hóa thông điệp lỗi HTTP `400/422/500` để frontend hiển thị rõ ràng cho user.
- [ ] Frontend: cập nhật `AddTaskModal` + `Dashboard` + `Todo Detail` để submit thật qua API, có `try...catch`, hiển thị lỗi và chỉ đóng form khi thành công.
- [ ] Verify backend: `cd backend && poetry run pytest -q`.
- [ ] Verify frontend: `cd frontend/todo-frontend && npm run lint && npm run build`.
- [ ] Verify Network (F12): kiểm tra Request URL, Payload, Status Code, Response Body cho thao tác Add Task.
- [ ] Viết test E2E Playwright Python cho flow Add Task theo chuẩn `backend/tests/run_e2e_test.py`.

### Task 07: Contract-First API Integration + E2E Reliability cho Todo CRUD (ưu tiên Add Task)

- [ ] Backend: Chuẩn hóa request/response schema cho `POST /api/v1/todos/`, `PUT /api/v1/todos/{id}`, `GET /api/v1/todos/`, `GET /api/v1/todos/{id}`.
- [ ] Backend: Đồng bộ response code/error message (`201`, `204`, `400/401/403/404/422/500`) theo contract nhất quán.
- [ ] Backend: Kiểm tra tương thích DB schema runtime, xử lý thiếu cột với fallback migration an toàn cho SQLite local.
- [ ] Backend: Xác minh middleware CSRF/cookie auth cho mọi request ghi dữ liệu (`POST/PUT/PATCH/DELETE`).
- [ ] Frontend: Đồng bộ mapping payload từ UI form theo contract (`title`, `description`, `priority`, `status`, `completed`, `due_date`, `thumbnail_url`, `is_vital`, `checklist_data`).
- [ ] Frontend: Chuẩn hóa toàn bộ điểm gọi Todo về endpoint `/api/v1/todos/...`, bổ sung `try...catch` và propagate lỗi đúng tầng.
- [ ] Frontend: Hoàn thiện UX submit (loading state, hiển thị lỗi thân thiện, chỉ đóng modal khi API thành công, tự refresh list/detail).
- [ ] Frontend: Loại bỏ dữ liệu không hợp lệ gửi lên API (ví dụ `blob:` URL local).
- [ ] Docs: Cập nhật `docs/TESTING_GUIDE.md` cho Task 7 với lệnh verify backend/frontend và checklist Network tab.
- [ ] E2E: Tạo test Playwright Python cho Add Task flow (cookie auth, random data, explicit waits, không dùng `time.sleep()`).
- [ ] Verify: Chạy và pass các lệnh:
  - [ ] `poetry run pytest -q`
  - [ ] `npm run lint`
  - [ ] `npm run build`
  - [ ] `poetry run python tests/e2e_task07_add_task_contract.py`

### BACKEND DEBT

- [x] WS /api/v1/notifications/ws — FE auth model dùng HttpOnly cookie (không đọc được JWT từ JS), nhưng BE WebSocket hiện bắt buộc `Authorization: Bearer <token>` header.
  - FE nguồn auth: `frontend/todo-frontend/src/features/auth/login/infrastructure/authRepository.js` (`getToken()` luôn trả `null`).
  - BE endpoint: `backend/src/todo_backend/api/routers/notifications.py`.
  - Done: đã bổ sung xác thực WS ưu tiên `access_token` từ cookie, fallback `Authorization` header để tương thích ngược.

- [ ] GET /api/v1/todos/search/ — contract query param không đồng bộ với FE filter/search hiện tại.
  - FE gửi `params` tổng quát (flow list dùng `q`, `status`, `view`, `sort_by`, ...): `frontend/todo-frontend/src/features/todos/infrastructure/todoRepository.js`.
  - BE `search_todos` chỉ nhận `title`, `completed`: `backend/src/todo_backend/api/routers/todos.py`.
  - Debt: chuẩn hóa `/search` để nhận `q` (và các filter cần thiết) **hoặc** loại bỏ endpoint `/search` cũ, chỉ giữ `GET /api/v1/todos/` làm nguồn query duy nhất.

- [ ] GET /api/v1/todos/search/ — semantic response mismatch khi không có dữ liệu.
  - BE hiện trả `404` với `"No todos found with the given criteria"`.
  - FE repository/search flow kỳ vọng danh sách (trống thì `[]`) để render empty-state.
  - Debt: đổi behavior sang `200` + `[]` để thống nhất contract list API.

- [ ] (Matrix đã đối chiếu, không nợ thêm) Các endpoint FE gọi và BE đã có tương ứng:
  - [ ] POST /auth/register
  - [ ] POST /auth/token
  - [ ] POST /auth/logout
  - [ ] GET /api/v1/todos/
  - [ ] POST /api/v1/todos/
  - [ ] GET /api/v1/todos/{id}
  - [ ] PUT /api/v1/todos/{id}
  - [ ] DELETE /api/v1/todos/{id}
  - [ ] GET /api/v1/task-categories/statuses
  - [ ] POST /api/v1/task-categories/statuses
  - [ ] PUT /api/v1/task-categories/statuses/{id}
  - [ ] DELETE /api/v1/task-categories/statuses/{id}
  - [ ] GET /api/v1/task-categories/priorities
  - [ ] POST /api/v1/task-categories/priorities
  - [ ] PUT /api/v1/task-categories/priorities/{id}
  - [ ] DELETE /api/v1/task-categories/priorities/{id}
  - [ ] GET /api/v1/chat/threads
  - [ ] POST /api/v1/chat/threads
  - [ ] DELETE /api/v1/chat/threads/{thread_id}
  - [ ] GET /api/v1/chat/threads/{thread_id}/messages
  - [ ] POST /api/v1/chat/
  - [ ] POST /api/v1/chat/voice

### Task 07: TDD & Fix Backend Debt - Cơ chế xác thực WebSocket với HttpOnly Cookie

- [x] Tạo test integration `backend/tests/test_websocket_auth.py` tái hiện flow login cookie -> connect websocket notifications.
- [x] Test dùng `POST /auth/register` để tạo user random.
- [x] Test dùng `POST /auth/token` để nhận cookie `access_token`.
- [x] Test kết nối `GET ws /api/v1/notifications/ws` chỉ với cookie (không gửi `Authorization` header).
- [x] Kỳ vọng theo target behavior: websocket kết nối thành công khi cookie hợp lệ.
- [x] Chạy đỏ vòng 1: `poetry run pytest -q tests/test_websocket_auth.py` (trước khi sửa backend).
- [x] Sửa backend ở `backend/src/todo_backend/api/routers/notifications.py` và verify lại test xanh.

### Task 09: Database Migration (SQLite to SQL Server)

- [ ] Backend infra: thêm SQL Server driver (`pyodbc`) vào `backend/pyproject.toml`.
- [ ] Backend infra: chuẩn hóa `DATABASE_URL` và engine theo dialect tại `backend/src/todo_backend/infrastructure/database/database.py`.
- [ ] Backend infra: chỉ dùng runtime fallback migration cho SQLite local, không ảnh hưởng SQL Server.
- [ ] Alembic: cập nhật `backend/src/todo_backend/alembic/env.py` để lấy `DATABASE_URL` từ env và normalize URL cho MSSQL.
- [ ] Alembic: bật `compare_type=True`, `compare_server_default=True`, `render_as_batch` chỉ khi SQLite.
- [ ] Migration cleanup: rà soát migration cũ SQLite trước khi phát hành SQL Server migration baseline.
- [ ] Lệnh tạo migration mới (manual): `alembic revision --autogenerate -m "init_sqlserver"`.
- [ ] Lệnh apply migration (manual): `alembic upgrade head`.

### Task 10: Deep Trace & Fix Silent Bugs (Frontend - Backend Sync) — Change Password

- [x] Trace Frontend flow tại `frontend/todo-frontend/src/app/profile/page.jsx` và `frontend/todo-frontend/src/features/user/components/ChangePasswordForm.jsx` để xác nhận submit đổi mật khẩu có gọi API thật hay không.
- [x] Trace Backend contract tại `backend/src/todo_backend/api/routers/user.py` + `backend/src/todo_backend/api/schemas/user_schema.py` để đối chiếu payload field name.
- [x] Trace persistence path tại `backend/src/todo_backend/app/usecases/user.py` + `backend/src/todo_backend/infrastructure/repositories/user_repository_impl.py` để xác nhận hash + commit.
- [x] Viết test TDD `backend/tests/test_change_password.py` theo flow: register -> login(old) -> change password -> login(new).
- [x] Chạy test đỏ vòng 1: `poetry run pytest -q tests/test_change_password.py`.
- [x] Chờ log đỏ từ user rồi mới vào bước fix backend/frontend.
- [x] Đồng bộ FE↔BE payload đổi mật khẩu (chấp nhận `currentPassword/newPassword` và snake_case tương thích).
- [x] Sửa usecase đổi mật khẩu để verify được hash Argon2 + bcrypt, tránh lỗi `UnknownHashError` gây 500.
- [x] Verify xanh: `python -m pytest -q tests/test_change_password.py`.

### Task 08: Deep Trace, TDD & Optimize - Tính năng Chat AI

- [x] Backend Trace: rà soát luồng lưu lịch sử chat qua `chat_threads` + `chat_messages` (create/append/list theo `thread_id`).
- [x] LLM Engine Audit: rà soát `AgentService` (LangChain/LangGraph), cơ chế memory theo `thread_id`, và trạng thái streaming text hiện tại.
- [x] API Router Audit: kiểm tra endpoint `/api/v1/chat/` dùng JSON response hay `StreamingResponse`/WebSocket.
- [x] Frontend Audit: kiểm tra luồng nhận phản hồi chat text có đọc stream (`getReader`) hay nhận JSON 1 lần.
- [x] TDD: tạo test `backend/tests/test_chat_ai.py` cho kịch bản memory cùng `thread_id`:
  - [x] Tạo user + login + tạo/nhận `thread_id`
  - [x] Gửi message 1: "Tên tôi là [RandomName]"
  - [x] Gửi message 2 cùng thread: "Tôi tên là gì?"
  - [x] Assert phản hồi message 2 chứa đúng `[RandomName]`
- [x] Verify backend: `cd backend && poetry run pytest -q tests/test_chat_ai.py`
- [x] Fix bug SQL Server boolean filter trong `chat_repository_impl.py`.
- [x] Backend streaming: thêm endpoint `POST /api/v1/chat/stream` trả `StreamingResponse` (`text/event-stream`) và persist assistant message sau stream.
- [x] Frontend resilience: cập nhật `/chat` để đọc stream qua `getReader()` + timeout/error handling thân thiện.
- [x] Runtime hotfix: thêm greeting fast-path + retry invoke trong `AgentService.run_text_command()` để giảm lỗi ngắt quãng từ LLM/network.
- [x] Verify frontend: `cd frontend/todo-frontend && npm run lint && npm run build`.
- [x] Tạo Playwright E2E script: `backend/tests/e2e_task08_chat_ai_stream.py`.

### Task 14: Fix LangGraph Async Checkpointer Error (Sau khi Migrate SQL Server)

- [x] Trace fallback checkpointer trong `backend/src/todo_backend/infrastructure/agent/dependencies.py`.
- [x] Xác nhận lỗi runtime `get_next_version` xuất phát từ fallback checkpointer cũ.
- [x] Thay fallback custom `InMemoryCheckpointer` sang `MemorySaver` chuẩn của LangGraph.
- [x] Cập nhật import: `from langgraph.checkpoint.memory import MemorySaver`.
- [x] Đảm bảo `get_checkpointer()` fallback trả `MemorySaver()` khi checkpointer không khả dụng.
- [x] Verify compile nhanh sau fix (không mở rộng scope sang test mới theo yêu cầu Task 14).

### Task 15: Implement BYOK (Gemini API Key động từ UI)

- [x] Trace frontend chat stream tại `frontend/todo-frontend/src/app/chat/page.jsx`.
- [x] Trace backend chat router tại `backend/src/todo_backend/api/routers/chat.py`.
- [x] Thêm header `X-Gemini-API-Key` vào endpoint AI (`/api/v1/chat/`, `/api/v1/chat/stream`, `/api/v1/chat/voice`, `/api/v1/agent/execute`).
- [x] Truyền `custom_api_key` xuyên suốt Router → AgentService.
- [x] Ưu tiên key runtime theo logic `custom_api_key or GEMINI_API_KEY` khi tạo executor/model.
- [x] Thêm UI nhập key + Save/Clear trên màn chat.
- [x] Lưu key vào `localStorage` và gắn header khi gọi `/api/v1/chat/stream`.
- [x] Verify backend: `poetry run pytest -q tests/test_chat_ai.py`.
- [x] Verify frontend: `npm run lint` và `npm run build`.
- [ ] Manual verify BYOK: nhập key rác (`12345`) để thấy lỗi key invalid, sau đó nhập key thật để chat hoạt động.

### Task 17: UI/UX Refactoring & Hoàn thiện Full Tính năng Chat

- [x] Dời UI BYOK khỏi màn Chat.
- [x] Tạo page Settings để nhập/lưu/xóa Gemini API key bằng `localStorage`.
- [x] Giữ luồng chat tự đọc key từ `localStorage` và gắn `X-Gemini-API-Key` khi gửi request stream.
- [x] Tích hợp Chat History thật: load `/api/v1/chat/threads`, click item để load `/api/v1/chat/threads/{thread_id}/messages`.
- [x] Đồng bộ `active_thread_id`/`thread_id` khi chọn lịch sử để tiếp tục đúng phiên chat cũ.
- [x] Thêm nút Upload File cạnh ô input chat + preview tên file đã chọn.
- [x] Sửa submit flow: nếu có file thì upload qua `/api/v1/chat/knowledge/upload` trước, sau đó stream chat theo text (nếu có).
- [x] Verify frontend: `npm run lint` và `npm run build`.
- [x] Tạo E2E Playwright Python: `backend/tests/e2e_task17_chat_history_upload.py`.
- [ ] Chạy manual/E2E verify Task 17 trên môi trường đang chạy backend + frontend.