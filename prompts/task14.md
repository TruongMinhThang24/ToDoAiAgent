# 🎯 Task 14: Fix LangGraph Async Checkpointer Error (Sau khi Migrate SQL Server)

## 1. Context
Sau khi đổi database sang SQL Server (dùng `pyodbc` - một sync driver), hệ thống LangGraph không tạo được async engine cho Checkpointer. Nó fallback về `InMemoryCheckpointer` nhưng bị crash với lỗi: `AttributeError: 'InMemoryCheckpointer' object has no attribute 'get_next_version'`.
Lỗi này xảy ra khi gọi `self.agent_executor.ainvoke` hoặc `astream`.

## 2. Requirements (Bắt buộc tuân thủ)

**BƯỚC 1: TRUY VẾT LỖI CHECKPOINTER**
- Bạn hãy mở file `backend/src/todo_backend/infrastructure/agent/dependencies.py` (hoặc file cấu hình LangGraph Agent của dự án).
- Tìm xem biến `checkpointer` đang được khởi tạo như thế nào khi fallback.

**BƯỚC 2: TIẾN HÀNH FIX BUG (THAY BẰNG MEMORYSAVER CHÍNH CHỦ)**
Từ các phiên bản LangGraph mới, `MemorySaver` là class chuẩn để lưu trữ trong bộ nhớ và hỗ trợ async hoàn hảo.
- Xóa class `InMemoryCheckpointer` tự chế hoặc cũ đi.
- Bổ sung import: `from langgraph.checkpoint.memory import MemorySaver`
- Cập nhật logic fallback: Khi không tạo được async DB checkpointer (do `pyodbc` không hỗ trợ async), hãy gán `checkpointer = MemorySaver()`.

HÀNH ĐỘNG CỦA BẠN BÂY GIỜ:
Nhả Code Block (Edit Proposal) để sửa file khởi tạo Dependencies/Agent của LangGraph. Sửa thẳng vào chỗ đang gọi fallback `InMemoryCheckpointer` thành `MemorySaver`. Không cần viết Test, nhả code Fix luôn để tôi Apply!