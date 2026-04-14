# 🎯 Task 10: Deep Trace & Fix Silent Bugs (Frontend - Backend Sync)

## 1. Context
Hệ thống vừa được chuyển sang SQL Server thành công. Tuy nhiên, dự án đang tồn tại các "Silent Failures" (Lỗi ngầm): thao tác trên UI báo thành công nhưng Database không lưu thay đổi. Chúng ta sẽ áp dụng TDD để fix từng tính năng một, bắt đầu với: **Change Password (Đổi mật khẩu)**.

## 2. Requirements (TDD Workflow)
Bạn BẮT BUỘC phải thực hiện truy vết theo luồng dọc (Vertical Slicing) từ Frontend xuống Backend và Database:

**BƯỚC 1: TRUY VẾT & PHÂN TÍCH (Change Password)**
- Đọc luồng code Frontend của tính năng Change Password: Hàm submit gọi API nào? Có catch lỗi đàng hoàng không?
- Đọc luồng code Backend: Payload (Pydantic model) có khớp không?
- Đọc luồng Database (Repository/UseCase): **TÌM XEM CÓ LỆNH `db.commit()` SAU KHI UPDATE PASSWORD CHƯA? CÓ HASH PASSWORD MỚI TRƯỚC KHI LƯU CHƯA?**

**BƯỚC 2: VIẾT TEST (NHỊP 1 CỦA TDD)**
- Viết 1 file test (VD: `backend/tests/test_change_password.py`) giả lập luồng: Đăng ký -> Đăng nhập -> Đổi mật khẩu -> Đăng nhập bằng mật khẩu MỚI.
- Xuất Code Block cho file Test này và yêu cầu tôi chạy. Chắc chắn sẽ thất bại vì lỗi ngầm hiện tại.

**BƯỚC 3: FIX BUG FULLSTACK (NHỊP 2 CỦA TDD - SAU KHI TÔI BÁO LỖI)**
- Chỉ sau khi nhận log lỗi từ tôi, bạn mới tiến hành sửa code Backend (thêm `commit()`, sửa logic hash) và Frontend (hiển thị thông báo chuẩn).
- Xuất các Code Block để tôi Apply.

HÀNH ĐỘNG CỦA BẠN BÂY GIỜ: 
Phân tích Bước 1 và thực hiện Bước 2. Nhả Code Block file Test E2E cho luồng Đổi Mật Khẩu để tôi chạy thử!