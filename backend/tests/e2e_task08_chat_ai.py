import asyncio
import os
import random
import string
import sys

import requests
from playwright.async_api import async_playwright


FRONTEND_URL = os.getenv("E2E_BASE_URL", "http://localhost:3000")
BACKEND_URL = os.getenv("E2E_BACKEND_URL", "http://localhost:8000")
CHAT_URL = f"{FRONTEND_URL}/chat"


def _random_suffix(length: int = 8) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def _assert_service_ready(url: str, service_name: str) -> None:
    response = requests.get(url, timeout=8)
    if not (200 <= response.status_code < 500):
        raise RuntimeError(f"{service_name} is not ready: {url} ({response.status_code})")


def _register_and_login() -> dict[str, str]:
    username = f"e2e_chat_ai_{_random_suffix()}"
    password = "admin12345"

    register_response = requests.post(
        f"{BACKEND_URL}/auth/register",
        json={
            "username": username,
            "email": f"{username}@example.com",
            "first_name": "E2E",
            "last_name": "ChatAI",
            "password": password,
            "phone_number": "0123456789",
        },
        timeout=10,
    )
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


def _fetch_latest_thread_id(cookies: dict[str, str]) -> str:
    response = requests.get(
        f"{BACKEND_URL}/api/v1/chat/threads",
        params={"limit": 1, "offset": 0},
        cookies=cookies,
        timeout=10,
    )
    if response.status_code != 200:
        raise RuntimeError(f"Cannot fetch chat threads: {response.status_code} - {response.text}")

    items = response.json().get("items", [])
    if not items:
        raise RuntimeError("No chat thread found after sending messages")

    thread_id = items[0].get("thread_id")
    if not thread_id:
        raise RuntimeError("Missing thread_id in thread list response")
    return thread_id


def _assert_thread_has_messages(cookies: dict[str, str], thread_id: str, expected_user_messages: list[str]) -> None:
    response = requests.get(
        f"{BACKEND_URL}/api/v1/chat/threads/{thread_id}/messages",
        params={"limit": 100, "offset": 0},
        cookies=cookies,
        timeout=10,
    )
    if response.status_code != 200:
        raise RuntimeError(f"Cannot fetch thread messages: {response.status_code} - {response.text}")

    items = response.json().get("items", [])
    contents = [item.get("content", "") for item in items]

    for text in expected_user_messages:
        if text not in contents:
            raise RuntimeError(f"Expected message not found in DB history: {text}")


async def main() -> None:
    print("🤖 Task08 E2E: Chat AI stream + thread persistence")

    _assert_service_ready(f"{FRONTEND_URL}/chat", "Frontend")
    _assert_service_ready(f"{BACKEND_URL}/health", "Backend")

    auth = _register_and_login()
    cookies = {
        "access_token": auth["access_token"],
        "csrf_token": auth["csrf_token"],
    }

    random_name = f"Name{_random_suffix(6)}"
    first_prompt = f"Tên tôi là {random_name}"
    second_prompt = "Tôi tên là gì?"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()

        await context.add_cookies(
            [
                {
                    "name": "access_token",
                    "value": auth["access_token"],
                    "url": FRONTEND_URL,
                    "sameSite": "Lax",
                },
                {
                    "name": "csrf_token",
                    "value": auth["csrf_token"],
                    "url": FRONTEND_URL,
                    "sameSite": "Lax",
                },
            ]
        )

        page = await context.new_page()

        try:
            await page.goto(CHAT_URL, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_url("**/chat", timeout=30000)

            input_box = page.get_by_placeholder("Type your message...")
            send_button = page.get_by_role("button", name="Send")

            await input_box.wait_for(state="visible", timeout=15000)

            # Message 1
            async with page.expect_response(lambda r: "/api/v1/chat/stream" in r.url and r.request.method == "POST"):
                await input_box.fill(first_prompt)
                await send_button.click()

            await page.get_by_text(first_prompt).first.wait_for(state="visible", timeout=15000)

            # Message 2 on same thread
            await input_box.fill(second_prompt)
            await send_button.click()
            await page.get_by_text(second_prompt).first.wait_for(state="visible", timeout=15000)

            thread_id = _fetch_latest_thread_id(cookies)
            _assert_thread_has_messages(cookies, thread_id, [first_prompt, second_prompt])

            print("✅ Task08 E2E passed")
            print(f"- user: {auth['username']}")
            print(f"- thread_id: {thread_id}")
            print(f"- random_name: {random_name}")

        finally:
            await context.close()
            await browser.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as exc:
        print(f"❌ Task08 E2E failed: {exc}")
        sys.exit(1)
