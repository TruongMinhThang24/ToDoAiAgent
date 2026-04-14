<!-- d:\Todos\thangtm25-Todos\Todos\prompts\task3.md -->
# 🎯 Task 04: Lọc + Sắp xếp + Tìm kiếm Todo trên màn hình danh sách

## 1. Context (Bối cảnh và Lý do)
Hiện tại Todo App đã có luồng tạo/sửa/xóa và phân tách inbox/archive, nhưng trải nghiệm sử dụng thực tế sẽ giảm mạnh khi số lượng task tăng vì người dùng chưa có bộ công cụ tìm kiếm, lọc và sắp xếp đầy đủ trên màn hình danh sách.  
Task này là ưu tiên cao nhất để hoàn thiện Core Features + UI/UX: giúp người dùng tìm đúng task nhanh, thao tác chính xác, giảm ma sát khi quản lý công việc hằng ngày.

## 2. Requirements (Yêu cầu chi tiết cho Frontend và Backend)

### 2.1. Functional Scope
Xây dựng bộ điều khiển danh sách Todo gồm:
- Tìm kiếm theo từ khóa (title/description).
- Lọc theo trạng thái:
  - Tất cả
  - Chưa hoàn thành
  - Đã hoàn thành
  - Quá hạn (nếu có due_date)
- Lọc theo chế độ hiển thị:
  - Inbox
  - Archived
- Sắp xếp theo:
  - Mới nhất
  - Cũ nhất
  - Hạn gần nhất
  - Hạn xa nhất
  - Ưu tiên cao trước (nếu có field priority)
- Cho phép reset toàn bộ bộ lọc về mặc định.

### 2.2. Frontend Requirements
#### A) UI/UX
- Thêm thanh tìm kiếm ở đầu danh sách Todo.
- Thêm nhóm filter chips/select rõ ràng, dễ thao tác trên desktop và mobile.
- Thêm dropdown sort.
- Trạng thái đang áp dụng filter/sort phải hiển thị trực quan.
- Có nút “Xóa bộ lọc” / “Reset”.
- Khi không có dữ liệu khớp điều kiện: hiển thị empty state thân thiện + CTA “Xóa bộ lọc”.

#### B) State & Data Flow
- Toàn bộ query state gồm: `q`, `status`, `view`, `sort_by`, `sort_order`, `page`, `page_size` (nếu có phân trang nội bộ).
- Query state phải đồng bộ URL (search params) để:
  - Reload vẫn giữ trạng thái.
  - Chia sẻ link giữ đúng bộ lọc/sắp xếp.
- Debounce tìm kiếm (300–500ms) để tránh spam request.
- Khi thay đổi filter/sort/search: reset `page` về 1 (nếu có paging).

#### C) Integration
- Tái sử dụng repository/service hiện có cho todos.
- Mọi request list todos phải truyền đúng query params theo state.
- Xử lý loading state mượt (skeleton/spinner nhỏ, không giật layout).
- Hiển thị lỗi dạng non-blocking nếu API fail (toast/message nhẹ).

### 2.3. Backend Requirements
#### A) API Contract
- Mở rộng endpoint lấy danh sách todos để nhận query params:
  - `q` (string)
  - `status` (all|active|completed|overdue)
  - `view` (inbox|archived|all)
  - `sort_by` (created_at|due_date|priority)
  - `sort_order` (asc|desc)
  - `page`, `page_size` (nếu đã có phân trang thì giữ tương thích)
- Thiết lập default rõ ràng nếu client không truyền.

#### B) Business Logic
- Search không phân biệt hoa thường.
- Kết hợp được nhiều điều kiện filter cùng lúc.
- Sort ổn định và nhất quán.
- Overdue chỉ áp dụng với task chưa hoàn thành và có due_date < now.
- Không phá vỡ hành vi cũ của endpoint (backward-compatible tối đa).

#### C) Validation & Error Handling
- Validate enum query params; trả lỗi 422 rõ ràng khi sai định dạng.
- Giới hạn `page_size` hợp lý để tránh response quá lớn.
- Trả metadata danh sách nhất quán cho frontend render (items, total, page, page_size).

### 2.4. Definition of Done (DoD)
- Người dùng có thể tìm/lọc/sắp xếp todo mượt ở UI.
- URL giữ đúng state sau reload.
- API trả dữ liệu đúng theo mọi tổ hợp điều kiện phổ biến.
- Không phát sinh regression cho create/update/delete/archive flow.
- Có test tối thiểu:
  - Backend: filter/search/sort combinations.
  - Frontend: query state + mapping params + empty state.

## 3. Constraints (Ràng buộc kỹ thuật)
- Bám theo kiến trúc hiện tại của dự án, không refactor lớn ngoài phạm vi task.
- Không triển khai các hạng mục tối ưu/bảo mật nâng cao trong task này (ví dụ: caching, rate limit, hardening bảo mật).
- Ưu tiên thay đổi nhỏ, rõ ràng, dễ review; giữ backward compatibility cho API cũ.
- Không thêm thư viện nặng nếu có thể tận dụng stack hiện có.
- UI phải responsive, không làm giảm trải nghiệm hiện tại trên mobile.