# Changelog

- 2026-03-20 — Checklist đánh dấu chức năng
	- Files: backend/src/todo_backend/app/usecases/agent_service.py; backend/tests/test_agent_service.py; .github/docs/PROJECT_CHECKLIST.md; .github/docs/CHANGELOG.md
	- Logic: Chọn invoke/ainvoke tùy checkpointer sync/async để tránh lỗi threading, thêm kiểm tra tool_calls an toàn, bổ sung unit test cho hai đường đi, cập nhật checklist & changelog.
