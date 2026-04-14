import random
import string
import sys
from pathlib import Path

import pytest
from starlette.websockets import WebSocketDisconnect
from fastapi.testclient import TestClient

# Ensure `backend/src` is importable when running `pytest` from backend root.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from main import app


def _random_suffix(length: int = 8) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def test_websocket_notifications_accepts_cookie_auth() -> None:
    """
    TDD NHỊP 1 (expected red with current backend):
    - Register + login to receive HttpOnly cookie `access_token`
    - Connect websocket `/api/v1/notifications/ws` without Authorization header
    - Expected target behavior: websocket should connect successfully using cookie auth

    Current backend only checks Authorization header, so this test should FAIL now.
    """
    username = f"ws_cookie_{_random_suffix()}"
    password = "admin12345"

    with TestClient(app) as client:
        register_response = client.post(
            "/auth/register",
            json={
                "username": username,
                "email": f"{username}@example.com",
                "first_name": "WS",
                "last_name": "Tester",
                "password": password,
                "phone_number": "0123456789",
            },
        )
        assert register_response.status_code == 201, register_response.text

        login_response = client.post(
            "/auth/token",
            data={"username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert login_response.status_code == 200, login_response.text
        assert client.cookies.get("access_token"), "Missing access_token cookie after login"

        # ❗ Không gửi Authorization header: chỉ dựa vào cookie session.
        # Target behavior (sau khi fix backend): websocket connect thành công.
        try:
            with client.websocket_connect("/api/v1/notifications/ws") as websocket:
                websocket.send_text("ping")
        except WebSocketDisconnect as exc:
            pytest.fail(
                f"WebSocket unexpectedly rejected cookie-authenticated client. code={exc.code}"
            )
