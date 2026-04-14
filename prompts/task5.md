# 🎯 Task N + 1 : Implement Structured Chat History + Thread Persistence (FE/BE)

## 1. Context (Bối cảnh và Lý do)
Hiện tại trải nghiệm Chat chưa dùng thực tế được vì lịch sử hội thoại chưa được lưu/khôi phục đầy đủ theo từng phiên (`thread_id`). Khi user refresh trang, đổi tab, hoặc quay lại sau, ngữ cảnh hội thoại bị mất, làm giảm mạnh chất lượng AI support và tỷ lệ giữ chân người dùng. Đây là gap lớn nhất so với một ứng dụng Todo có trợ lý AI “production-ready”.

## 2. Requirements (Yêu cầu chi tiết cho Frontend và Backend)

### 2.1 Backend Requirements
1. **Thiết kế dữ liệu hội thoại có cấu trúc**
   - Lưu được: `thread_id`, `user_id`, `role` (`user`/`assistant`/`system`), `content`, `metadata` (optional), `created_at`.
   - Mỗi message phải truy vết được theo user và thread.

2. **API quản lý thread và history**
   - `GET /chat/threads` (danh sách thread của user, phân trang).
   - `GET /chat/threads/{thread_id}/messages` (lấy lịch sử theo thứ tự thời gian, phân trang hoặc cursor).
   - `POST /chat/threads` (tạo thread mới).
   - `DELETE /chat/threads/{thread_id}` (xóa hoặc soft-delete thread).

3. **Tích hợp gửi chat theo thread**
   - Endpoint chat hiện tại phải nhận/duy trì `thread_id`.
   - Nếu không có `thread_id`, backend tạo mới và trả về.
   - Bảo đảm message mới được append đúng thread.

4. **Security & data isolation**
   - Chỉ user sở hữu mới truy cập được thread/messages của mình.
   - Validate input, giới hạn độ dài message, sanitize text cơ bản.

5. **Reliability**
   - Thêm index cho truy vấn theo `(user_id, thread_id, created_at)`.
   - Có handling rõ ràng cho thread không tồn tại hoặc không thuộc user.

### 2.2 Frontend Requirements
1. **Thread-aware chat state**
   - `useChat` quản lý `currentThreadId`, danh sách thread, message map theo thread.
   - Persist `currentThreadId` (URL query hoặc localStorage) để reload không mất ngữ cảnh.

2. **UI thread list (sidebar hoặc panel)**
   - Hiển thị danh sách hội thoại gần nhất (title preview + thời gian cập nhật).
   - Cho phép: tạo hội thoại mới, chuyển thread, xóa thread.

3. **Load history khi vào thread**
   - Khi chọn thread: gọi API history, render đầy đủ theo thứ tự.
   - Có loading skeleton, empty state, và error state rõ ràng.

4. **Gửi tin nhắn ổn định theo thread**
   - Khi gửi message, luôn gắn `thread_id` hiện tại.
   - UI optimistic update (nếu cần), rollback khi lỗi.

5. **UX polish tối thiểu**
   - Auto-scroll xuống message mới.
   - Disable input khi đang gửi.
   - Thông báo lỗi thân thiện khi request thất bại.

### 2.3 QA / Acceptance Criteria
1. Reload trang vẫn thấy đúng thread đang mở và lịch sử tương ứng.
2. Chuyển qua lại 2+ thread không bị lẫn message.
3. User A không đọc được thread của User B.
4. Xóa thread xong không còn hiển thị ở list và không truy cập được history cũ.
5. Test API + E2E cơ bản pass cho luồng: tạo thread → chat → reload → khôi phục → xóa.

## 3. Constraints (Ràng buộc kỹ thuật)
1. **Không phá vỡ API cũ**: Nếu đang có endpoint chat cũ, cần backward-compatible hoặc có migration plan rõ ràng.
2. **Giữ kiến trúc hiện tại**: Tuân thủ layer/domain/usecase/repository hiện có; không hardcode logic vào router/component.
3. **Hiệu năng**: Không load toàn bộ history vô hạn; bắt buộc phân trang/cursor với thread dài.
4. **Bảo mật**: Tuân thủ cơ chế auth/cookie hiện tại, tuyệt đối không để lộ dữ liệu cross-user.
5. **Khả năng mở rộng**: Thiết kế sẵn cho streaming response và message metadata trong phase sau.
