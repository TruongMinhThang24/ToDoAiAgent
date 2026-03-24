import asyncio
import os
import random
import string
import sys
import time

import requests
from playwright.async_api import async_playwright


FRONTEND_URL = os.getenv("E2E_BASE_URL", "http://localhost:3000")
BACKEND_URL = os.getenv("E2E_BACKEND_URL", "http://localhost:8000")
CHAT_URL = f"{FRONTEND_URL}/chat"


def _wait_service_ready(url: str, timeout_seconds: int = 25) -> bool:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            response = requests.get(url, timeout=3)
            if 200 <= response.status_code < 500:
                return True
        except requests.RequestException:
            pass
        time.sleep(1)
    return False


def _random_user() -> str:
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"e2e_chat_{suffix}"


def _create_and_login_user() -> dict[str, str]:
    username = _random_user()
    password = "admin12345"

    register_payload = {
        "username": username,
        "email": f"{username}@example.com",
        "first_name": "E2E",
        "last_name": "Chat",
        "password": password,
        "phone_number": "0123456789",
    }
    register_response = requests.post(f"{BACKEND_URL}/auth/register", json=register_payload, timeout=10)
    if register_response.status_code not in (200, 201):
        raise RuntimeError(f"Register failed: {register_response.status_code} - {register_response.text}")

    login_response = requests.post(
        f"{BACKEND_URL}/auth/token",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10,
    )
    if login_response.status_code != 200:
        raise RuntimeError(f"Login failed: {login_response.status_code} - {login_response.text}")

    access_token = login_response.cookies.get("access_token")
    csrf_token = login_response.cookies.get("csrf_token")
    if not access_token:
        raise RuntimeError("Missing access_token cookie after login")

    return {
        "username": username,
        "password": password,
        "access_token": access_token,
        "csrf_token": csrf_token or "",
    }


def _wait_message_persisted(access_token: str, csrf_token: str, thread_id: str, expected_text: str, timeout_seconds: int = 20) -> bool:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            response = requests.get(
                f"{BACKEND_URL}/api/v1/chat/threads/{thread_id}/messages",
                params={"limit": 200, "offset": 0},
                cookies={"access_token": access_token, "csrf_token": csrf_token},
                timeout=5,
            )
            if response.status_code == 200:
                items = response.json().get("items", [])
                if any((item.get("content") or "") == expected_text for item in items):
                    return True
        except requests.RequestException:
            pass
        time.sleep(1)
    return False


async def _wait_thread_id_from_local_storage(page, timeout_seconds: int = 12) -> str | None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        thread_id = await page.evaluate("() => localStorage.getItem('todo_chat_current_thread_id')")
        if thread_id:
            return thread_id
        await page.wait_for_timeout(500)
    return None


def _get_latest_thread_id(access_token: str, csrf_token: str) -> str | None:
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/v1/chat/threads",
            params={"limit": 1, "offset": 0},
            cookies={"access_token": access_token, "csrf_token": csrf_token},
            timeout=8,
        )
        if response.status_code != 200:
            return None
        items = response.json().get("items", [])
        if not items:
            return None
        return items[0].get("thread_id")
    except requests.RequestException:
        return None


async def main():
    print("🤖 Task05 E2E: chat thread persistence...")

    if not _wait_service_ready(f"{FRONTEND_URL}/login"):
        raise RuntimeError("Frontend not ready")
    if not _wait_service_ready(f"{BACKEND_URL}/health"):
        raise RuntimeError("Backend not ready")

    user = _create_and_login_user()
    print(f"ℹ️ User: {user['username']}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()

        cookie_items = [
            {"name": "access_token", "value": user["access_token"], "url": FRONTEND_URL, "sameSite": "Lax"},
        ]
        if user.get("csrf_token"):
            cookie_items.append(
                {"name": "csrf_token", "value": user["csrf_token"], "url": FRONTEND_URL, "sameSite": "Lax"}
            )

        await context.add_cookies(cookie_items)
        page = await context.new_page()

        try:
            # 1) Open chat
            await page.goto(CHAT_URL, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_url("**/chat", timeout=30000)

            # 2) Create thread from UI
            await page.get_by_role("button", name="New Chat").click()
            await page.wait_for_timeout(800)

            # 3) Send message in created thread
            test_message = f"Task05 persistence test {int(time.time())}"
            input_box = page.get_by_placeholder("Nhập tin nhắn hoặc ghi âm...")
            await input_box.fill(test_message)
            await page.get_by_role("button", name="Send").click()

            # Verify message persisted in backend (ổn định hơn chờ UI text)
            current_thread_id = await _wait_thread_id_from_local_storage(page, timeout_seconds=12)
            if not current_thread_id:
                # Fallback: đọc thread mới nhất từ API khi localStorage bị trễ/mất đồng bộ
                fallback_thread_id = _get_latest_thread_id(
                    access_token=user["access_token"],
                    csrf_token=user["csrf_token"],
                )
                if fallback_thread_id:
                    current_thread_id = fallback_thread_id
                    print("⚠️ localStorage chưa có thread_id, dùng fallback từ API")
                else:
                    raise RuntimeError("Thread id was not persisted to localStorage")

            persisted = _wait_message_persisted(
                access_token=user["access_token"],
                csrf_token=user["csrf_token"],
                thread_id=current_thread_id,
                expected_text=test_message,
                timeout_seconds=20,
            )
            if not persisted:
                raise RuntimeError("Message was not persisted to thread messages API")

            # UI smoke check (non-blocking strict): user text should appear somewhere
            await page.get_by_text(test_message).first.wait_for(state="visible", timeout=20000)

            # 4) Reload and verify thread/message restored
            await page.reload(wait_until="domcontentloaded")
            await page.wait_for_timeout(1000)
            restored_thread_id = await _wait_thread_id_from_local_storage(page, timeout_seconds=10)
            if restored_thread_id != current_thread_id:
                raise RuntimeError("Thread id not restored correctly after reload")

            # Sau reload, xác nhận lại data từ API trước
            persisted_after_reload = _wait_message_persisted(
                access_token=user["access_token"],
                csrf_token=user["csrf_token"],
                thread_id=current_thread_id,
                expected_text=test_message,
                timeout_seconds=20,
            )
            if not persisted_after_reload:
                raise RuntimeError("Message not found in API after reload")

            await page.get_by_text(test_message).first.wait_for(state="visible", timeout=20000)

            # 5) Delete thread from sidebar
            delete_button = page.get_by_role("button", name="Xóa").first
            await delete_button.click()
            await page.wait_for_timeout(1000)

            # verify deleted thread is no longer returned by API
            api_response = requests.get(
                f"{BACKEND_URL}/api/v1/chat/threads",
                cookies={"access_token": user["access_token"], "csrf_token": user["csrf_token"]},
                timeout=10,
            )
            if api_response.status_code != 200:
                raise RuntimeError(f"Threads API failed: {api_response.status_code}")
            thread_ids = [item["thread_id"] for item in api_response.json().get("items", [])]
            if current_thread_id in thread_ids:
                raise RuntimeError("Deleted thread still present in list")

            print("✅ Task05 E2E passed")
            print(f"- thread_id: {current_thread_id}")
            print(f"- message: {test_message}")

        finally:
            await context.close()
            await browser.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as exc:
        print(f"❌ Task05 E2E failed: {exc}")
        sys.exit(1)
