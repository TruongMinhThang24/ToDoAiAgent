# 🎯 Task 09: Database Migration (SQLite to SQL Server)

## 1. Context
Dự án hiện đang dùng SQLite cho Backend. Để chuẩn bị cho môi trường Production, chúng ta cần chuyển đổi toàn bộ cấu hình Database (SQLAlchemy + Alembic) sang Microsoft SQL Server.

## 2. Requirements (Tuân thủ MASTER AI WORKFLOW)
**NHỊP 1: CẬP NHẬT INFRASTRUCTURE (BACKEND)**
- Quét các file `requirements.txt` / `pyproject.toml`, thêm thư viện driver cho SQL Server (khuyến nghị `pyodbc` hoặc `pymssql`).
- Sửa file cấu hình Database (thường là `backend/src/todo_backend/core/database.py` hoặc `config.py`): Đổi chuỗi kết nối (Connection String) sang định dạng của SQL Server. Hỗ trợ đọc từ biến môi trường `DATABASE_URL`.
- Điều chỉnh các Model SQLAlchemy nếu có kiểu dữ liệu không tương thích giữa SQLite và SQL Server (VD: độ dài của chuỗi String, kiểu Boolean).

**NHỊP 2: CẬP NHẬT ALEMBIC MIGRATION**
- Cập nhật `alembic/env.py` để tương thích với SQL Server dialect.
- Xóa các file migration cũ của SQLite (nếu cần thiết để làm sạch) và in ra câu lệnh để tôi chạy tạo file migration mới (`alembic revision --autogenerate -m "init_sqlserver"`).

HÀNH ĐỘNG CỦA BẠN (PHASE 1 - PLAN):
- In ra Checklist các file cấu hình Database và Model cần sửa.
- Nhả Code Block cập nhật các file đó. (Không cần viết Test cho task này vì đây là config hạ tầng).