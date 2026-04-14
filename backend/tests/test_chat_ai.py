import random
import re
import string
import sys
from pathlib import Path

from fastapi import Depends
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# Ensure `backend/src` is importable when running pytest from backend root.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from main import app
from todo_backend.api.routers import chat as chat_router_module
from todo_backend.api.schemas.chat_schema import AgentChatReponse
from todo_backend.domain.entities.models import ChatMessage


class FakeMemoryAgentService:
    """Fake agent to keep test deterministic and validate DB-backed memory flow.

    The real endpoint persists user messages before agent execution.
    This fake agent reads persisted messages from `chat_messages` by `thread_id`
    and answers memory questions from that history.
    """

    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    async def run_text_command(
        self,
        user_query: str,
        thread_id: str,
        custom_api_key: str | None = None,
    ) -> AgentChatReponse:
        lowered = (user_query or "").strip().lower()

        if "tôi tên là gì" in lowered:
            history = (
                self.db.query(ChatMessage)
                .filter(
                    ChatMessage.owner_id == self.user_id,
                    ChatMessage.thread_id == thread_id,
                    ChatMessage.role == "user",
                )
                .order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc())
                .all()
            )

            remembered_name = None
            for msg in history:
                match = re.search(r"tên tôi là\s+(.+)$", (msg.content or "").strip(), re.IGNORECASE)
                if match:
                    remembered_name = match.group(1).strip(" .,!?:;\"'")

            if remembered_name:
                friendly_message = f"Bạn tên là {remembered_name}."
            else:
                friendly_message = "Mình chưa biết tên của bạn trong luồng chat này."

            return AgentChatReponse(
                friendly_message=friendly_message,
                thread_id=thread_id,
                needs_clarification=False,
                clarification_prompt=None,
            )

        return AgentChatReponse(
            friendly_message="Mình đã lưu thông tin của bạn.",
            thread_id=thread_id,
            needs_clarification=False,
            clarification_prompt=None,
        )


def _random_suffix(length: int = 8) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def _register_user(client: TestClient, username: str, password: str) -> None:
    response = client.post(
        "/auth/register",
        json={
            "username": username,
            "email": f"{username}@example.com",
            "first_name": "Chat",
            "last_name": "Memory",
            "password": password,
            "phone_number": "0123456789",
        },
    )
    assert response.status_code == 201, response.text


def _login(client: TestClient, username: str, password: str) -> str:
    response = client.post(
        "/auth/token",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200, response.text

    csrf_token = client.cookies.get("csrf_token")
    assert csrf_token, "Missing csrf_token cookie after login"
    return csrf_token


async def _override_agent_service(
    db: Session = Depends(chat_router_module.get_db),
    user: dict = Depends(chat_router_module.get_current_user),
):
    return FakeMemoryAgentService(db=db, user_id=user["id"])


def test_chat_ai_memory_same_thread_returns_user_name() -> None:
    """TDD scenario for task 8: memory must work inside the same thread_id."""
    username = f"chat_ai_{_random_suffix()}"
    password = "admin12345"
    random_name = f"Name{_random_suffix(6)}"

    with TestClient(app) as client:
        _register_user(client, username, password)
        csrf_token = _login(client, username, password)

        app.dependency_overrides[chat_router_module.get_agent_service] = _override_agent_service

        try:
            # 1) Message 1: introduce name and receive thread_id.
            first_response = client.post(
                "/api/v1/chat/",
                json={"message": f"Tên tôi là {random_name}", "thread_id": None},
                headers={"X-CSRF-Token": csrf_token},
            )
            assert first_response.status_code == 200, first_response.text

            first_payload = first_response.json()
            thread_id = first_payload.get("thread_id")
            assert thread_id, "Missing thread_id after first chat message"

            # 2) Message 2: ask memory question in the same thread.
            second_response = client.post(
                "/api/v1/chat/",
                json={"message": "Tôi tên là gì?", "thread_id": thread_id},
                headers={"X-CSRF-Token": csrf_token},
            )
            assert second_response.status_code == 200, second_response.text

            second_payload = second_response.json()
            assistant_text = second_payload.get("friendly_message", "")

            # 3) Critical assertion: response must contain the random name.
            assert random_name in assistant_text, (
                f"Expected assistant response to contain '{random_name}', got: {assistant_text}"
            )

            # Optional DB persistence assertion: history endpoint contains both user messages.
            history_response = client.get(f"/api/v1/chat/threads/{thread_id}/messages")
            assert history_response.status_code == 200, history_response.text
            contents = [item.get("content", "") for item in history_response.json().get("items", [])]
            assert any(f"Tên tôi là {random_name}" == text for text in contents)
            assert any("Tôi tên là gì?" == text for text in contents)
        finally:
            app.dependency_overrides.pop(chat_router_module.get_agent_service, None)


def test_chat_ai_stream_endpoint_returns_sse_events() -> None:
    """Ensure backend exposes text streaming endpoint for chat responses."""
    username = f"chat_stream_{_random_suffix()}"
    password = "admin12345"

    with TestClient(app) as client:
        _register_user(client, username, password)
        csrf_token = _login(client, username, password)

        app.dependency_overrides[chat_router_module.get_agent_service] = _override_agent_service

        try:
            response = client.post(
                "/api/v1/chat/stream",
                json={"message": "Tên tôi là StreamName", "thread_id": None},
                headers={"X-CSRF-Token": csrf_token},
            )
            assert response.status_code == 200, response.text
            assert response.headers.get("content-type", "").startswith("text/event-stream")
            assert '"type": "chunk"' in response.text
            assert '"type": "done"' in response.text
        finally:
            app.dependency_overrides.pop(chat_router_module.get_agent_service, None)
