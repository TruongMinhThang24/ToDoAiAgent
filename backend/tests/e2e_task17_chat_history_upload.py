import asyncio
import os
import random
import string
import sys
import tempfile
import time

import requests
from playwright.async_api import async_playwright


FRONTEND_URL = os.getenv("E2E_BASE_URL", "http://localhost:3000")
BACKEND_URL = os.getenv("E2E_BACKEND_URL", "http://localhost:8000")
CHAT_URL = f"{FRONTEND_URL}/chat"


def _wait_service_ready(url: str, timeout_seconds: int = 30) -> bool:
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


def _random_suffix(length: int = 8) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def _create_and_login_user() -> dict[str, str]:
    username = f"e2e_t17_{_random_suffix()}"
    password = "admin12345"

    register_payload = {
        "username": username,
        "email": f"{username}@example.com",
        "first_name": "E2E",
        "last_name": "Task17",
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
        "access_token": access_token,
        "csrf_token": csrf_token or "",
    }


async def main() -> None:
    print("🤖 Task17 E2E: settings-route + chat-history + upload")

    if not _wait_service_ready(f"{BACKEND_URL}/health"):
        raise RuntimeError("Backend not ready")
    if not _wait_service_ready(f"{FRONTEND_URL}/chat"):
        raise RuntimeError("Frontend not ready")

    session = _create_and_login_user()
    first_message = f"Task17-first-{_random_suffix(5)}"
    second_message = f"Task17-second-{_random_suffix(5)}"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as tmp:
        tmp.write("Task17 upload file content")
        upload_path = tmp.name

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            cookies = [
                {"name": "access_token", "value": session["access_token"], "url": FRONTEND_URL, "sameSite": "Lax"},
            ]
            if session["csrf_token"]:
                cookies.append(
                    {"name": "csrf_token", "value": session["csrf_token"], "url": FRONTEND_URL, "sameSite": "Lax"}
                )
            await context.add_cookies(cookies)

            # 1) Settings page is routable
            await page.goto(f"{FRONTEND_URL}/settings", wait_until="domcontentloaded", timeout=30000)
            await page.get_by_text("Your Gemini API Key").wait_for(state="visible", timeout=15000)

            # 2) Chat first thread message
            await page.goto(CHAT_URL, wait_until="domcontentloaded", timeout=30000)
            input_box = page.get_by_placeholder("Type your message...")
            await input_box.wait_for(state="visible", timeout=15000)

            await input_box.fill(first_message)
            await page.get_by_role("button", name="Send").click()
            await page.get_by_text(first_message).first.wait_for(state="visible", timeout=30000)

            # 3) Create new thread and send second message
            await page.get_by_role("button", name="New Chat").click()
            await input_box.fill(second_message)
            await page.get_by_role("button", name="Send").click()
            await page.get_by_text(second_message).first.wait_for(state="visible", timeout=30000)

            # 4) Click history item for first thread and ensure old message reloads
            first_history_btn = page.locator("button", has_text=first_message).first
            await first_history_btn.wait_for(state="visible", timeout=30000)
            await first_history_btn.click()
            await page.get_by_text(first_message).first.wait_for(state="visible", timeout=30000)

            # 5) Upload file and submit (without text)
            file_input = page.locator("input[type='file']")
            await file_input.set_input_files(upload_path)
            await page.get_by_role("button", name="Send").click()
            await page.get_by_text("Đã tải tài liệu").first.wait_for(state="visible", timeout=30000)

            print("✅ Task17 E2E passed")
        finally:
            await context.close()
            await browser.close()
            try:
                os.remove(upload_path)
            except OSError:
                pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as exc:
        print(f"❌ Task17 E2E failed: {exc}")
        sys.exit(1)
