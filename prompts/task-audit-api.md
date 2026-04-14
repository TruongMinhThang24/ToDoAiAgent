# 🎯 Task: Fullstack Gap Analysis (Frontend vs Backend API)

## 1. Context
Hiện tại Frontend đã phát triển rất nhiều UI và các hàm gọi API (repositories/services), nhưng Backend chưa code kịp các endpoint tương ứng. Cần lập một bản đồ chi tiết để biết chính xác Backend đang nợ Frontend những API nào.

## 2. Requirements
Bạn là Senior Architect. Hãy quét toàn bộ thư mục Frontend (đặc biệt là các file gọi API bằng axios/fetch) và thư mục Backend (các file Router/Controller).

HÀNH ĐỘNG CỦA BẠN (PHASE 1):
1. Đối chiếu URL, HTTP Method (GET, POST, PUT, DELETE) và Payload mà Frontend đang gọi với các endpoint Backend đang có.
2. Lập ra một danh sách "API MISSING" (Những API Frontend gọi nhưng Backend chưa có hoặc sai param).
3. BẮT BUỘC: Mở file `docs/PROJECT_CHECKLIST.md` và tạo một heading `### BACKEND DEBT`. Viết toàn bộ danh sách API còn thiếu này dưới dạng Checklist `[ ]`.
4. Nhả Code Block (Edit Proposal) cho file `PROJECT_CHECKLIST.md` để tôi bấm Apply! Đừng nói mồm!