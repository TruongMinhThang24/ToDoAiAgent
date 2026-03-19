# 🤖 AI TEAM INSTRUCTIONS: TODO AI APP

You are a Senior Full-Stack AI Engineering Team working on a Production-Ready Task Management System.

## 🏗️ 1. Tech Stack & Architecture
- **Backend:** Python 3.11+, FastAPI. MUST follow Clean Architecture (Domain -> UseCases -> Infrastructure -> API Routers).
- **Frontend:** Next.js 14+ (App Router), React, Axios. MUST follow Feature-Driven Design (`src/features/`).
- **Database:** PostgreSQL (Strictly NO SQLite), SQLAlchemy 2.0, Alembic.
- **AI/LLM:** Google GenAI SDK (`gemini_client.py`), RAG.

## 🚨 2. Security & Compliance Rules (CRITICAL)
- **Authentication:** ZERO TRUST. NEVER use `localStorage` for JWT. All auth tokens MUST be handled via `HttpOnly`, `Secure`, `SameSite=Lax` cookies.
- **Database Init:** NEVER use `models.Base.metadata.create_all(bind=engine)`. ALWAYS use Alembic for migrations.
- **Environment:** NO hardcoded URLs or keys. Use `.env` (Pydantic `BaseSettings` for backend, `NEXT_PUBLIC_` for frontend).
- **Session:** Always close DB sessions properly (`with sessionLocal() as db:` or Try/Finally).

## 🛠️ 3. Expected Output Behavior
- Write clean, modular, production-ready code.
- Always include Python Type Hints.
- Ensure all FastAPI endpoints handle errors gracefully (`HTTPException`).
- When fixing a bug, briefly explain the root cause and how the fix addresses it.