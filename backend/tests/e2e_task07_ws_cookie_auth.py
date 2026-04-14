import asyncio
import os
import random
import string
import sys
import time
from urllib.parse import urlparse

import requests
import websockets
from websockets.exceptions import InvalidStatus, WebSocketException


BACKEND_URL = os.getenv("E2E_BACKEND_URL", "http://localhost:8000")
PASSWORD = os.getenv("E2E_PASSWORD", "admin12345")
USERNAME = os.getenv("E2E_USERNAME")


def _random_suffix(length: int = 8) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def _wait_service_ready(url: str, timeout_seconds: int = 25) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            response = requests.get(url, timeout=3)
            if 200 <= response.status_code < 500:
                return
        except requests.RequestException:
            pass
        time.sleep(1)

    raise RuntimeError(f"Service not ready: {url}")


def _ensure_test_account() -> tuple[str, str]:
    if USERNAME:
        return USERNAME, PASSWORD

    username = f"e2e_ws_{_random_suffix()}"
    payload = {
        "username": username,
        "email": f"{username}@example.com",
        "first_name": "E2E",
        "last_name": "WS",
        "password": PASSWORD,
        "phone_number": "0123456789",
    }

    response = requests.post(f"{BACKEND_URL}/auth/register", json=payload, timeout=10)
    if response.status_code not in (200, 201):
        raise RuntimeError(
            f"Cannot create test user. status={response.status_code}, body={response.text}"
        )

    return username, PASSWORD


def _login_and_get_cookies(username: str, password: str) -> dict[str, str]:
    response = requests.post(
        f"{BACKEND_URL}/auth/token",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Login failed. status={response.status_code}, body={response.text}"
        )

    access_token = response.cookies.get("access_token")
    csrf_token = response.cookies.get("csrf_token")
    if not access_token:
        raise RuntimeError("Missing access_token cookie from /auth/token")

    return {
        "access_token": access_token,
        "csrf_token": csrf_token or "",
    }


def _build_ws_url() -> str:
    parsed = urlparse(BACKEND_URL)
    scheme = "wss" if parsed.scheme == "https" else "ws"
    host = parsed.netloc
    return f"{scheme}://{host}/api/v1/notifications/ws"


async def _assert_ws_rejects_without_cookie(ws_url: str) -> None:
    try:
        async with websockets.connect(ws_url):
            # Nếu connect được ở đây là sai kỳ vọng bảo mật.
            raise RuntimeError("WebSocket unexpectedly accepted anonymous connection")
    except InvalidStatus:
        # Expected: server should reject unauthenticated websocket.
        return
    except WebSocketException:
        # Some servers may close immediately instead of handshake reject.
        return


async def _assert_ws_accepts_with_cookie(ws_url: str, cookies: dict[str, str]) -> None:
    cookie_header = f"access_token={cookies['access_token']}"
    if cookies.get("csrf_token"):
        cookie_header += f"; csrf_token={cookies['csrf_token']}"

    async with websockets.connect(
        ws_url,
        additional_headers={"Cookie": cookie_header},
    ) as ws:
        # Server không gửi message chủ động, chỉ cần giữ kết nối + gửi ping text.
        await ws.send("ping")
        await asyncio.sleep(0.2)


async def main() -> None:
    print("🔎 Running E2E Task07 - WebSocket Cookie Auth...")

    _wait_service_ready(f"{BACKEND_URL}/health")

    username, password = _ensure_test_account()
    cookies = _login_and_get_cookies(username, password)
    ws_url = _build_ws_url()

    await _assert_ws_rejects_without_cookie(ws_url)
    await _assert_ws_accepts_with_cookie(ws_url, cookies)

    print("✅ E2E PASSED")
    print(f"- user: {username}")
    print(f"- ws_url: {ws_url}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as exc:
        print(f"\n❌ E2E FAILED: {exc}")
        sys.exit(1)
