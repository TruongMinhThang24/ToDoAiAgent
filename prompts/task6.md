# 🎯 Task 6 : Debug & Fix luồng kết nối API (Frontend - Backend) cho tính năng [Tên tính năng, VD: Add Task]

## 1. Context (Bối cảnh và Lý do)
Hiện tại giao diện Frontend cho tính năng [Tên tính năng] đã hoàn thiện rất tốt. Tuy nhiên, khi thao tác (VD: bấm nút Submit/Save), dữ liệu không được đẩy xuống Backend thành công hoặc Backend trả về lỗi nhưng Frontend không bắt được.
Cần một Senior Fullstack Engineer rà soát lại toàn bộ luồng gọi API từ lúc user click chuột ở Frontend cho đến khi dữ liệu vào DB ở Backend để tìm ra điểm đứt gãy.

## 2. Requirements (Yêu cầu chi tiết cho Frontend và Backend)
**Rà soát Backend:**
- Kiểm tra file Router/Controller: Đã mở CORS chưa? Endpoint URL có khớp chuẩn với Frontend đang gọi không?
- Kiểm tra Pydantic Schema / DTO: Payload Frontend gửi lên có bị thiếu trường (field) hay sai kiểu dữ liệu (data type) so với Backend yêu cầu không?
- Xử lý Exception: Backend phải trả về HTTP Status Code chuẩn (400, 422, 500) kèm message rõ ràng thay vì crash ngầm.

**Rà soát Frontend:**
- Kiểm tra file gọi API (Repository/Service): Đảm bảo URL gọi đúng cổng của Backend (VD: `http://localhost:8000/api/...`). Đảm bảo truyền đúng Headers (Content-Type: application/json, Authorization nếu có).
- Xử lý State/UI: Phải có khối `try...catch`. Bắt được lỗi từ Backend thì phải hiện Toast/Alert thông báo cho user. Nếu thành công (20x) phải update lại state danh sách và đóng Form.

## 3. Constraints (Ràng buộc kỹ thuật)
- KHÔNG viết lại toàn bộ UI, chỉ sửa đúng logic hàm call API (`handleSubmit`, `fetchData`,...).
- TUÂN THỦ ĐIỀU LUẬT TỐI THƯỢNG: Phải xuất Code Block để tôi bấm Apply.
- Ở Phase 3 (VERIFY), hãy hướng dẫn tôi mở tab Network (F12) trên trình duyệt để kiểm tra Payload và Response.

## 4. Bằng chứng Lỗi (ERROR LOGS - RẤT QUAN TRỌNG)
[BẠN HÃY DÁN LỖI MÀU ĐỎ TRONG CONSOLE TRÌNH DUYỆT (F12) HOẶC LỖI TRÊN TERMINAL BACKEND VÀO ĐÂY. NẾU KHÔNG CÓ, HÃY XÓA MỤC NÀY]