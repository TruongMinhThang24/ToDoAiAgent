# Project TODOs

This file lists unfinished, in-progress, and completed tasks for the project with links to the related files.

## Unfinished / To do

- **Add unit & integration tests (backend):** Create tests for CRUD, chat, agent tools, and RAG integration. See [backend/check.md](backend/check.md) and [backend/pyproject.toml](backend/pyproject.toml).
- **Replace hardcoded ffmpeg path:** Make ffmpeg configurable via env/config and ensure container-friendly audio processing. See [backend/src/todo_backend/api/routers/chat.py](backend/src/todo_backend/api/routers/chat.py).
- **RAG integration tests & docs:** Finish RAG wiring, add tests and documentation. See [backend/src/todo_backend/app/usecases/rag.py](backend/src/todo_backend/app/usecases/rag.py) and [backend/src/todo_backend/infrastructure/agent/tools.py](backend/src/todo_backend/infrastructure/agent/tools.py).
- **Integrate LangSmith tracing:** Add initialization and env var documentation. See [backend/check.md](backend/check.md) and [backend/pyproject.toml](backend/pyproject.toml).
- **Add structured chat history endpoint:** Backend endpoint to return threaded/metadata-rich chat histories. See [backend/src/todo_backend/api/routers/chat.py](backend/src/todo_backend/api/routers/chat.py).

## In-progress / Needs verification

- **Implement chat history threading:** Ensure backend stores and returns `thread_id` and update frontend consumer. See [backend/src/todo_backend/api/routers/chat.py](backend/src/todo_backend/api/routers/chat.py) and [frontend/todo-frontend/src/features/chat/infrastructure/chatRepository.js](frontend/todo-frontend/src/features/chat/infrastructure/chatRepository.js).
- **Improve audio validation & conversion:** Support webm/opus, robust MIME handling, and consistent FE/BE checks. See [backend/src/todo_backend/api/routers/chat.py](backend/src/todo_backend/api/routers/chat.py) and [frontend/todo-frontend/src/features/chat/infrastructure/chatRepository.js](frontend/todo-frontend/src/features/chat/infrastructure/chatRepository.js).

## Completed / Implemented (reference)

- **Todo CRUD (with due_date):** Backend schemas and usecases for todos implemented. See [backend/src/todo_backend/api/schemas/todos_schema.py](backend/src/todo_backend/api/schemas/todos_schema.py) and [backend/src/todo_backend/app/usecases/todos.py](backend/src/todo_backend/app/usecases/todos.py).
- **Agent tools factory:** Tools for add/list/update/delete/search implemented. See [backend/src/todo_backend/infrastructure/agent/tools.py](backend/src/todo_backend/infrastructure/agent/tools.py).
- **Basic audio upload and voice chat endpoint:** Implemented in backend and frontend. See [backend/src/todo_backend/api/routers/chat.py](backend/src/todo_backend/api/routers/chat.py) and [frontend/todo-frontend/src/features/chat/infrastructure/chatRepository.js](frontend/todo-frontend/src/features/chat/infrastructure/chatRepository.js).

---

If you'd like, I can:

- Create a Git branch and commit this file.
- Open PR scaffolding and add CI test skeleton.
- Start implementing one of the `not-started` tasks (pick one).

Generated: TODO list tracked via assistant tool.
