# 🎯 Task 7 : Contract-First API Integration + E2E Reliability cho Todo CRUD (ưu tiên Add Task)

## 1. Context (Bối cảnh và Lý do)
Luồng cốt lõi Add Task đã chạy được nhưng vẫn có rủi ro lệch contract giữa Frontend và Backend (payload, kiểu dữ liệu, field optional/required, status code, CSRF/cookie auth), dẫn đến lỗi khó truy vết khi đổi schema hoặc refactor UI.
Để app vận hành thực tế ổn định, cần chuẩn hóa API contract theo hướng "contract-first", đồng bộ toàn bộ điểm gọi FE/BE, và khóa chất lượng bằng test E2E tự động cho các đường đi quan trọng.

## 2. Requirements (Yêu cầu chi tiết cho Frontend và Backend)

### Backend
- Chuẩn hóa schema request/response cho Todo:
  - `POST /api/v1/todos/`
  - `PUT /api/v1/todos/{id}`
  - `GET /api/v1/todos/`
  - `GET /api/v1/todos/{id}`
- Đảm bảo response code và error message nhất quán:
  - 201 cho create thành công
  - 204 cho update/delete thành công
  - 400/401/403/404/422/500 trả message rõ ràng, không crash ngầm
- Kiểm tra tương thích DB schema runtime:
  - Không phát sinh lỗi thiếu cột khi database cũ
  - Có fallback migration an toàn cho môi trường local SQLite
- Đảm bảo middleware CSRF/cookie auth hoạt động đúng với mọi request ghi dữ liệu (POST/PUT/PATCH/DELETE).

### Frontend
- Đồng bộ payload từ UI form về đúng backend contract:
  - Mapping đúng `title`, `description`, `priority`, `status`, `completed`, `due_date`, `thumbnail_url`, `is_vital`, `checklist_data`
- Chuẩn hóa repository/hook:
  - Tất cả điểm gọi Todo dùng cùng endpoint chuẩn `/api/v1/todos/...`
  - Có `try...catch`, propagate lỗi đúng tầng
- UX khi submit:
  - Hiển thị loading state trên nút submit
  - Hiển thị lỗi thân thiện (inline + alert/toast)
  - Chỉ đóng modal khi API thành công
  - Tự refresh danh sách/chi tiết sau create hoặc update
- Loại bỏ dữ liệu không hợp lệ gửi lên API (ví dụ blob URL local không dùng được server-side).

### Testing & Verification
- Cập nhật `docs/TESTING_GUIDE.md` cho Task 7:
  - Lệnh backend/frontend verify
  - Checklist kiểm tra Network tab (F12)
- Tạo E2E Playwright Python cho flow:
  - Login bằng cookie auth
  - Add Task từ UI
  - Assert task xuất hiện trong dashboard/list
  - Handle timeout/retry hợp lý, không dùng `time.sleep()` cứng

## 3. Constraints (Ràng buộc kỹ thuật)
- Không rewrite UI lớn; chỉ sửa logic integration, validation, và error handling cần thiết.
- Tuân thủ kiến trúc hiện có:
  - Frontend: feature-driven + repository/hook
  - Backend: router/schema/usecase/repository
- Giữ tương thích ngược cho dữ liệu cũ và môi trường local.
- Mọi thay đổi phải đi kèm verify:
  - Backend: `poetry run pytest -q`
  - Frontend: `npm run lint` và `npm run build`
  - E2E: `poetry run python tests/e2e_task07_add_task_contract.py`
# 🎯 Task 7 : Contract-First API Integration + E2E Reliability cho Todo CRUD (ưu tiên Add Task)

## 1. Context (Bối cảnh và Lý do)
Luồng cốt lõi Add Task đã chạy được nhưng vẫn có rủi ro lệch contract giữa Frontend và Backend (payload, kiểu dữ liệu, field optional/required, status code, CSRF/cookie auth), dẫn đến lỗi khó truy vết khi đổi schema hoặc refactor UI.
Để app vận hành thực tế ổn định, cần chuẩn hóa API contract theo hướng “contract-first”, đồng bộ toàn bộ điểm gọi FE/BE, và khóa chất lượng bằng test E2E tự động cho các đường đi quan trọng.

## 2. Requirements (Yêu cầu chi tiết cho Frontend và Backend)

### Backend
- Chuẩn hóa schema request/response cho Todo:
  - `POST /api/v1/todos/`
  - `PUT /api/v1/todos/{id}`
  - `GET /api/v1/todos/`
  - `GET /api/v1/todos/{id}`
- Đảm bảo response code và error message nhất quán:
  - 201 cho create thành công
  - 204 cho update/delete thành công
  - 400/401/403/404/422/500 trả message rõ ràng, không crash ngầm
- Kiểm tra tương thích DB schema runtime:
  - Không phát sinh lỗi thiếu cột khi database cũ
  - Có fallback migration an toàn cho môi trường local SQLite
- Đảm bảo middleware CSRF/cookie auth hoạt động đúng với mọi request ghi dữ liệu (POST/PUT/PATCH/DELETE).

### Frontend
- Đồng bộ payload từ UI form về đúng backend contract:
  - Mapping đúng `title`, `description`, `priority`, `status`, `completed`, `due_date`, `thumbnail_url`, `is_vital`, `checklist_data`
- Chuẩn hóa repository/hook:
  - Tất cả điểm gọi Todo dùng cùng endpoint chuẩn `/api/v1/todos/...`
  - Có `try...catch`, propagate lỗi đúng tầng
- UX khi submit:
  - Hiển thị loading state trên nút submit
  - Hiển thị lỗi thân thiện (inline + alert/toast)
  - Chỉ đóng modal khi API thành công
  - Tự refresh danh sách/chi tiết sau create hoặc update
- Loại bỏ dữ liệu không hợp lệ gửi lên API (ví dụ blob URL local không dùng được server-side).

### Testing & Verification
- Cập nhật `docs/TESTING_GUIDE.md` cho Task 7:
  - Lệnh backend/frontend verify
  - Checklist kiểm tra Network tab (F12)
- Tạo E2E Playwright Python cho flow:
  - Login bằng cookie auth
  - Add Task từ UI
  - Assert task xuất hiện trong dashboard/list
  - Handle timeout/retry hợp lý, không dùng `time.sleep()` cứng

## 3. Constraints (Ràng buộc kỹ thuật)
- Không rewrite UI lớn; chỉ sửa logic integration, validation, và error handling cần thiết.
- Tuân thủ kiến trúc hiện có:
  - Frontend: feature-driven + repository/hook
  - Backend: router/schema/usecase/repository
- Giữ tương thích ngược cho dữ liệu cũ và môi trường local.
- Mọi thay đổi phải đi kèm verify:
  - Backend: `poetry run pytest -q`
  - Frontend: `npm run lint` và `npm run build`
  - E2E: `poetry run python tests/e2e_task07_*.py`