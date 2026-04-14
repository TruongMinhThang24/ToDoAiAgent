# TESTING GUIDE

## Task 03: Implement CSRF Protection for Cookie-based Authentication

### 1) Backend automated checks

- Run in backend folder with your working Poetry environment:
  - `poetry run ruff check src/`
  - `poetry run pytest -q`

Expected:
- Ruff: `All checks passed!`
- Pytest: existing tests pass (no new regressions).

### 2) Frontend automated checks

- Run in frontend folder:
  - `npm run lint`
  - `npm run build`

Expected:
- Lint pass.
- Build pass.

### 3) Manual security tests (required)

#### Case A — Valid flow should succeed
1. Open browser and login normally.
2. Go to Todos page.
3. Create a todo, update a todo, delete a todo.

Expected:
- All write actions succeed.
- In DevTools > Application > Cookies, both `access_token` and `csrf_token` exist after login.

#### Case B — Missing CSRF header should be blocked
1. Login.
2. Open DevTools > Console.
3. Execute a write request manually **without** `X-CSRF-Token` header while keeping cookies.

Expected:
- Response is `403`.
- Response detail is exactly: `CSRF token missing or invalid`.

#### Case C — Mismatched CSRF token should be blocked
1. Login.
2. Send a POST/PUT/PATCH/DELETE request with a fake `X-CSRF-Token` value.

Expected:
- Response is `403`.
- Response detail is exactly: `CSRF token missing or invalid`.

#### Case D — Logout must clear both cookies
1. Login.
2. Click Logout.
3. Inspect cookies.

Expected:
- `access_token` removed.
- `csrf_token` removed.
- User is redirected to login.

### 4) Regression checks

- `/auth/me` still works when logged in.
- GET endpoints (read-only) still work without CSRF header.
- Chat/todos/user/admin write endpoints require valid CSRF when auth cookie is present.

---

## Task 04: Lọc + Sắp xếp + Tìm kiếm Todo trên màn hình danh sách

### 1) Backend automated checks

- Run in backend folder:
  - `poetry run pytest -q`

Expected:
- Test suite passes.
- No regression in existing auth/todo/chat tests.

### 2) Frontend automated checks

- Run in frontend folder:
  - `npm run lint`
  - `npm run build`

Expected:
- Lint pass.
- Build pass.

### 3) Manual functional tests (required)

#### Case A — Search by keyword
1. Login and open `/todos`.
2. Ensure there are at least 3 todos with different title/description.
3. Type keyword in search box (e.g. part of title).
4. Wait ~400ms debounce.

Expected:
- List is filtered by keyword.
- URL contains `q=`.

#### Case B — Filter by status
1. In todos page, switch status filter:
   - All
   - Active
   - Completed
   - Overdue

Expected:
- List updates correctly for each status.
- URL updates `status=`.

#### Case C — Switch Inbox / Archive tab with same filter state
1. Apply search + status filter.
2. Switch tab between `inbox` and `archive`.

Expected:
- `view=` in URL updates accordingly.
- Data in each tab stays consistent with current filters.

#### Case D — Sorting
1. Change sort field: `Newest` / `Due date` / `Priority`.
2. Change sort order `Desc` / `Asc`.

Expected:
- List order changes correctly.
- URL includes `sort_by` and `sort_order`.

#### Case E — Reset filters
1. Apply search + filter + sort.
2. Click `Reset filters` (or `Clear filters` in empty state).

Expected:
- Search/filter/sort returns default state.
- URL params are cleared back to default.

#### Case F — Pagination controls
1. Ensure enough todos to exceed one page.
2. Use `Next` and `Prev` buttons.

Expected:
- Page indicator changes.
- URL includes `page=` when page > 1.
- Correct page data is shown.

### 4) API smoke checks (optional via browser DevTools)

- Verify request query string to `/api/v1/todos/` includes:
  - `q`, `status`, `view`, `sort_by`, `sort_order`, `page`, `page_size`
- Verify response shape contains:
  - `items`, `total`, `page`, `page_size`

---

## Task 05: Structured Chat History + Thread Persistence

### 1) Backend automated checks

- Run in backend folder:
  - `poetry run pytest -q`
  - `poetry run python -m py_compile src/todo_backend/api/routers/chat.py src/todo_backend/api/schemas/chat_schema.py src/todo_backend/app/usecases/chat_thread_service.py src/todo_backend/infrastructure/repositories/chat_repository_impl.py src/todo_backend/domain/entities/models.py`

Expected:
- Existing backend tests pass.
- Modified chat/thread modules compile without syntax errors.

### 2) Frontend automated checks

- Run in frontend folder:
  - `npm run lint`
  - `npm run build`

Expected:
- Lint pass.
- Build pass.

### 3) E2E automation (Playwright Python)

- Run in backend folder (with frontend/backend servers running):
  - `poetry run python tests/e2e_task05_chat_threads.py`

What this test covers:
1. Login bằng cookie auth.
2. Mở trang chat và tạo thread mới.
3. Gửi 1 tin nhắn trong thread đó.
4. Reload trang và xác nhận thread/message được khôi phục.
5. Xóa thread và xác nhận thread không còn trong API list.

---

## Task 06: Debug & Fix Add Task API Flow (Frontend - Backend)

### 1) Backend automated checks

- Run in backend folder:
  - `poetry run pytest -q`

Expected:
- Existing backend tests pass.
- No regression in auth/csrf/todos routes.

### 2) Frontend automated checks

- Run in frontend folder:
  - `npm run lint`
  - `npm run build`

Expected:
- Lint pass.
- Build pass.

### 3) Manual browser verification (F12 Network)

1. Login and open `/dashboard`.
2. Click `ADD TASK`.
3. Fill title/date/description and click `Done`.
4. Open DevTools > Network and inspect request `POST /api/v1/todos/`.

Expected:
- Request URL: `http://localhost:8000/api/v1/todos/`
- Request headers include:
  - `Content-Type: application/json`
  - `X-CSRF-Token` (for write requests)
- Response status: `201 Created`
- New task appears on dashboard list.

When failing:
- UI shows clear error message (alert + inline error in modal).
- Modal remains open so user can retry.

### 4) E2E automation (Playwright Python)

- Run in backend folder (frontend + backend must be running):
  - `poetry run python tests/e2e_task06_add_task_api.py`

Flow covered:
1. Ensure services are ready.
2. Create/register test user (or use provided env credentials).
3. Login via API and inject auth cookies.
4. Open dashboard, submit Add Task modal.
5. Verify modal closes and created task appears in UI.

---

## Task 07: Contract-First API Integration + E2E Reliability (Todo CRUD - Add Task first)

### 1) Backend automated checks

- Run in backend folder:
  - `poetry run pytest -q`

Expected:
- Tests pass.
- No regression for auth/csrf/todos.
- Todo create response is `201` and update/delete are `204`.

### 2) Frontend automated checks

---

## Task 08: Deep Trace, TDD & Optimize - Chat AI

### 1) Backend automated checks

- Run in backend folder:
  - `poetry run pytest -q tests/test_chat_ai.py`

Expected:
- Test memory flow cùng `thread_id` pass.
- Test endpoint stream `/api/v1/chat/stream` trả `text/event-stream` pass.

### 2) Frontend automated checks

- Run in frontend folder:
  - `npm run lint`
  - `npm run build`

---

## Task 08: Deep Trace, TDD & Optimize - Chat AI

### 1) Backend automated checks

- Run in backend folder:
  - `poetry run pytest -q tests/test_chat_ai.py`

Expected:
- `test_chat_ai_memory_same_thread_returns_user_name` passes.
- Memory behavior is validated in the same `thread_id`.

### 2) Frontend automated checks

- Run in frontend folder:
  - `npm run lint`
  - `npm run build`

Expected:
- Lint pass.
- Build pass.

### 3) E2E automation (Playwright Python)

- Run in backend folder (frontend + backend must be running):
  - `poetry run python tests/e2e_task08_chat_ai_stream.py`

Flow covered:
1. Register user and login bằng API (`/auth/register`, `/auth/token`).
2. Inject auth cookies vào browser context (bypass UI login).
3. Open `/chat`, click `New Chat`.
4. Send message 1: `Tên tôi là <random_name>`.
5. Send message 2: `Tôi tên là gì?`.
6. Assert response hiển thị `<random_name>` trên UI.

### 4) Streaming + timeout manual smoke checks

1. Open `/chat` and send a normal message.
2. Verify assistant text appears incrementally (stream typing effect).
3. Simulate bad network / stop backend and send a message.

Expected:
- UI does not crash.
- User sees friendly fallback message for timeout/network error.

Expected:
- Lint pass.
- Build pass.

### 3) E2E automation (Playwright Python)

- Run in backend folder (frontend + backend must be running):
  - `poetry run python tests/e2e_task08_chat_ai.py`

Flow covered:
1. Tạo user random qua `POST /auth/register`.
2. Login qua `POST /auth/token`, inject `access_token` + `csrf_token` vào browser context.
3. Mở `/chat`, gửi 2 message liên tiếp.
4. Verify request stream `/api/v1/chat/stream` hoạt động.
5. Verify DB history chứa đủ 2 user message trong cùng thread.

- Run in frontend folder:
  - `npm run lint`
  - `npm run build`

Expected:
- Lint pass.
- Build pass.

### 3) Browser Network checklist (F12) for Add Task

1. Login and open `/dashboard`.
2. Click `ADD TASK`, fill required fields, click `Done`.
3. Inspect `POST /api/v1/todos/` request in Network.

Checklist expected:
- Request URL is `http://localhost:8000/api/v1/todos/`.
- Request method is `POST`.
- Request headers contain:
  - `Content-Type: application/json`
  - `X-CSRF-Token` (with cookie auth flow)
- Request payload contract contains fields:
  - `title`, `description`, `priority`, `status`, `completed`, `due_date`, `thumbnail_url`, `is_vital`, `checklist_data`
- Payload must not contain local `blob:` URL in `thumbnail_url`.
- Response status is `201 Created` and response body contains created todo.
- On failure, modal stays open and user sees inline error message.

### 4) E2E automation (Playwright Python)

- Run in backend folder (frontend + backend must be running):
  - `poetry run python tests/e2e_task07_add_task_contract.py`

Flow covered:
1. Wait frontend/backend readiness.
2. Register random user and login via `/auth/token`.
3. Inject cookie auth into browser context.
4. Open dashboard and create task from UI.
5. Assert created task appears in dashboard list.

---

## Task 07 (WS Auth Debt): TDD xác thực WebSocket bằng HttpOnly Cookie

### 1) Backend TDD test

- Run in backend folder:
  - `poetry run pytest -q tests/test_websocket_auth.py`

Expected:
- Test pass.
- WebSocket `/api/v1/notifications/ws` chấp nhận kết nối khi client đã login và có cookie `access_token`.
- Không bắt buộc `Authorization` header cho flow cookie-auth.

---

## Task 10: Deep Trace & Fix Silent Bugs — Change Password

### 1) Backend regression test (required)

- Run in backend folder:
  - `python -m pytest -q tests/test_change_password.py`

Expected:
- Test pass (`1 passed`).
- Flow phải đi qua đầy đủ: register -> login(old) -> change password -> login(new).

### 2) Contract expectations

- Endpoint: `PUT /user/change_password`
- Auth: cookie `access_token` + header `X-CSRF-Token`.
- Accepted payload keys:
  - camelCase: `currentPassword`, `newPassword`
  - snake_case (compatible): `current_password`, `new_password`

Expected:
- Success trả `204 No Content`.
- Sai mật khẩu cũ trả `401 Incorrect password`.

---

## Task 15: Implement BYOK (Gemini API Key động từ UI)

### 1) Backend automated checks

- Run in backend folder:
  - `poetry run pytest -q tests/test_chat_ai.py`

Expected:
- Chat regression tests pass sau khi thêm tham số `custom_api_key` xuyên suốt router/service.

### 2) Frontend automated checks

- Run in frontend folder:
  - `npm run lint`
  - `npm run build`

Expected:
- Lint pass.
- Build pass.

### 3) Manual BYOK checks (required)

1. Restart backend + frontend.
2. Mở trang `/chat`.
3. Ở khung `Your Gemini API Key`, nhập `12345` rồi bấm `Save`.
4. Gửi một tin nhắn chat.

Expected:
- Backend nhận header `X-Gemini-API-Key`.
- Chat trả lỗi key không hợp lệ (xác nhận BYOK path hoạt động đúng).

5. Bấm `Clear`, nhập Gemini key hợp lệ của bạn, bấm `Save`.
6. Gửi lại tin nhắn chat.

Expected:
- AI trả lời bình thường qua `/api/v1/chat/stream`.
- Không cần sửa `.env` cho từng user key nữa.

---

## Task 17: UI/UX Refactoring & Hoàn thiện Full Tính năng Chat

### 1) Frontend automated checks

- Run in frontend folder:
  - `npm run lint`
  - `npm run build`

Expected:
- Lint pass.
- Build pass.

### 2) Manual functional checks

1. Open `/settings`, confirm BYOK form hiển thị và Save/Clear hoạt động.
2. Open `/chat`, xác nhận không còn khối BYOK trong chat header.
3. Send message để tạo thread mới.
4. Click một thread ở sidebar Chat History.

Expected:
- Tin nhắn cũ của thread được load lại.
- Tin nhắn gửi tiếp theo bám đúng thread vừa chọn.

5. Ở `/chat`, chọn file bằng nút đính kèm cạnh ô nhập.
6. Click `Send` khi chỉ có file.

Expected:
- File upload thành công qua `/api/v1/chat/knowledge/upload`.
- Chat hiển thị message xác nhận đã tải tài liệu.

### 3) E2E automation (Playwright Python)

- Run in backend folder (frontend + backend must be running):
  - `poetry run python tests/e2e_task17_chat_history_upload.py`

Flow covered:
1. Login bằng API và inject cookie vào browser context.
2. Mở `/settings` và xác nhận form BYOK.
3. Mở `/chat`, gửi message thread 1.
4. Tạo thread mới, gửi message thread 2.
5. Click lại history thread 1 và verify message cũ xuất hiện.
6. Upload file từ UI và verify message xác nhận upload.
