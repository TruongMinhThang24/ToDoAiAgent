import asyncio
import os
import random
import string
import sys
from typing import Dict

import requests
from playwright.async_api import async_playwright


FRONTEND_URL = os.getenv("E2E_BASE_URL", "http://127.0.0.1:3000")
BACKEND_URL = os.getenv("E2E_BACKEND_URL", "http://127.0.0.1:8000")
CHAT_URL = f"{FRONTEND_URL}/chat"


def _random_text(prefix: str, length: int = 8) -> str:
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=length))
    return f"{prefix}_{suffix}"


async def _wait_service_ready(url: str, timeout_seconds: int = 30) -> bool:
    deadline = asyncio.get_running_loop().time() + timeout_seconds
    while asyncio.get_running_loop().time() < deadline:
        try:
            response = requests.get(url, timeout=3)
            if 200 <= response.status_code < 500:
                return True
        except requests.RequestException:
            pass
        await asyncio.sleep(1)
    return False


async def _pick_ready_base_url(candidates: list[str], health_path: str, timeout_seconds: int = 15) -> str | None:
    for base_url in candidates:
        if await _wait_service_ready(f"{base_url}{health_path}", timeout_seconds=timeout_seconds):
            return base_url
    return None


def _register_and_login(backend_url: str) -> Dict[str, str]:
    username = _random_text("e2e_chat_ai")
    password = "admin12345"

    register_payload = {
        "username": username,
        "email": f"{username}@example.com",
        "first_name": "E2E",
        "last_name": "ChatAI",
        "password": password,
        "phone_number": "0123456789",
    }
    register_response = requests.post(f"{backend_url}/auth/register", json=register_payload, timeout=10)
    if register_response.status_code not in (200, 201):
        raise RuntimeError(f"Register failed: {register_response.status_code} - {register_response.text}")

    login_response = requests.post(
        f"{backend_url}/auth/token",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10,
    )
    if login_response.status_code != 200:
        raise RuntimeError(f"Login failed: {login_response.status_code} - {login_response.text}")

    access_token = login_response.cookies.get("access_token")
    csrf_token = login_response.cookies.get("csrf_token")
    if not access_token:
        raise RuntimeError("Missing access_token cookie from /auth/token")

    return {
        "username": username,
        "access_token": access_token,
        "csrf_token": csrf_token or "",
    }


async def main() -> None:
    print("🤖 Task08 E2E: Chat AI stream + memory")

    backend_candidates = [BACKEND_URL]
    if "127.0.0.1" not in BACKEND_URL:
        backend_candidates.append("http://127.0.0.1:8000")
    if "localhost" not in BACKEND_URL:
        backend_candidates.append("http://localhost:8000")

    frontend_candidates = [FRONTEND_URL]
    if "127.0.0.1" not in FRONTEND_URL:
        frontend_candidates.append("http://127.0.0.1:3000")
    if "localhost" not in FRONTEND_URL:
        frontend_candidates.append("http://localhost:3000")

    ready_backend_url = await _pick_ready_base_url(backend_candidates, "/health")
    if not ready_backend_url:
        raise RuntimeError(
            "Backend is not ready. Checked: " + ", ".join(f"{u}/health" for u in backend_candidates)
        )

    ready_frontend_url = await _pick_ready_base_url(frontend_candidates, "/chat")
    if not ready_frontend_url:
        raise RuntimeError(
            "Frontend is not ready. Checked: " + ", ".join(f"{u}/chat" for u in frontend_candidates)
        )

    frontend_url = ready_frontend_url
    backend_url = ready_backend_url
    chat_url = f"{frontend_url}/chat"

    session = _register_and_login(backend_url)
    random_name = _random_text("Name", length=6)
    print(f"ℹ️ user={session['username']} | expected_name={random_name}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            cookie_items = [
                {"name": "access_token", "value": session["access_token"], "url": frontend_url, "sameSite": "Lax"},
            ]
            if session.get("csrf_token"):
                cookie_items.append(
                    {"name": "csrf_token", "value": session["csrf_token"], "url": frontend_url, "sameSite": "Lax"}
                )

            await context.add_cookies(cookie_items)

            await page.goto(chat_url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_url("**/chat", timeout=30000)

            # Step 1: start new chat thread.
            await page.get_by_role("button", name="New Chat").click()

            # Step 2: send "Tên tôi là <random>".
            input_box = page.get_by_placeholder("Type your message...")
            await input_box.wait_for(state="visible", timeout=15000)
            await input_box.fill(f"Tên tôi là {random_name}")
            await page.get_by_role("button", name="Send").click()

            # Wait for first assistant answer to finish rendering.
            await page.get_by_role("button", name="Send").wait_for(state="visible", timeout=20000)

            # Step 3: ask memory question in same thread.
            await input_box.fill("Tôi tên là gì?")
            await page.get_by_role("button", name="Send").click()

            # Step 4: assert streamed answer eventually contains random_name.
            expected_locator = page.get_by_text(random_name)
            await expected_locator.first.wait_for(state="visible", timeout=45000)

            print("✅ Task08 E2E passed")
            print(f"- memory answer contains: {random_name}")
        finally:
            await context.close()
            await browser.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as exc:
        print(f"❌ Task08 E2E failed: {exc}")
        sys.exit(1)
