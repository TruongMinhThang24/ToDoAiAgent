import sys
import uuid
from pathlib import Path

from fastapi.testclient import TestClient

# Ensure backend/src is importable for pytest collection.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from main import app


def _register_user(client: TestClient, username: str, password: str) -> None:
    payload = {
        "username": username,
        "email": f"{username}@example.com",
        "first_name": "Silent",
        "last_name": "Bug",
        "password": password,
        "phone_number": "0123456789",
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 201, response.text


def _login(client: TestClient, username: str, password: str):
    return client.post(
        "/auth/token",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )


def test_change_password_vertical_slice_from_frontend_payload() -> None:
    """
    TDD round-1 for Silent Bug task.

    Intentionally uses frontend-like payload keys (`currentPassword`, `newPassword`)
    to expose FE/BE contract mismatch and ensure it is visible by test.
    """
    username = f"cp_{uuid.uuid4().hex[:10]}"
    old_password = f"OldPass!{uuid.uuid4().hex[:8]}"
    new_password = f"NewPass!{uuid.uuid4().hex[:8]}"

    with TestClient(app) as client:
        _register_user(client, username, old_password)

        login_old = _login(client, username, old_password)
        assert login_old.status_code == 200, login_old.text

        csrf_token = client.cookies.get("csrf_token")
        assert csrf_token, "Missing csrf_token cookie after login"

        # Frontend form field names (camelCase) - expected to fail with current BE schema.
        change_payload = {
            "currentPassword": old_password,
            "newPassword": new_password,
        }
        change_response = client.put(
            "/user/change_password",
            json=change_payload,
            headers={"X-CSRF-Token": csrf_token},
        )

        # Desired behavior for fullstack sync is success; current state should fail (red test).
        assert change_response.status_code == 204, (
            f"Expected 204 from /user/change_password but got "
            f"{change_response.status_code}: {change_response.text}"
        )

    with TestClient(app) as fresh_client:
        login_new = _login(fresh_client, username, new_password)
        assert login_new.status_code == 200, (
            f"Expected login with new password to succeed, got "
            f"{login_new.status_code}: {login_new.text}"
        )
