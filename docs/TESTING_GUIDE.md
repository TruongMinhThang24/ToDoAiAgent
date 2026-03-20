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
