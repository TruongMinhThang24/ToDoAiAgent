import asyncio
import os
import random
import string
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from playwright.async_api import async_playwright

# Ensure `backend/src` is importable when running from backend root.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from todo_backend.app.usecases.scheduler import check_due_todos

BASE_URL = os.getenv("E2E_BASE_URL", "http://localhost:3000")
BACKEND_URL = os.getenv("E2E_BACKEND_URL", "http://localhost:8000")
DASHBOARD_URL = f"{BASE_URL}/dashboard"
PASSWORD = os.getenv("E2E_PASSWORD", "admin12345")


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


def _register_and_login() -> tuple[str, dict[str, str]]:
    username = f"e2e_task23_{_random_suffix()}"
    payload = {
        "username": username,
        "email": f"{username}@example.com",
        "first_name": "E2E",
        "last_name": "Task23",
        "password": PASSWORD,
        "phone_number": "0123456789",
    }

    register_response = requests.post(f"{BACKEND_URL}/auth/register", json=payload, timeout=10)
    if register_response.status_code not in (200, 201):
        raise RuntimeError(
            f"Cannot create test user. status={register_response.status_code}, body={register_response.text}"
        )

    login_response = requests.post(
        f"{BACKEND_URL}/auth/token",
        data={"username": username, "password": PASSWORD},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10,
    )
    if login_response.status_code != 200:
        raise RuntimeError(f"Login failed. status={login_response.status_code}, body={login_response.text}")

    access_token = login_response.cookies.get("access_token")
    csrf_token = login_response.cookies.get("csrf_token")
    if not access_token:
        raise RuntimeError("Missing access_token cookie from /auth/token")

    return username, {
        "access_token": access_token,
        "csrf_token": csrf_token or "",
    }


def _create_due_soon_todo(cookies: dict[str, str]) -> int:
    due_date = (datetime.now(timezone.utc) + timedelta(minutes=10)).replace(microsecond=0).isoformat()
    payload = {
        "title": f"Task23 Scheduler {_random_suffix(6)}",
        "description": "Todo for scheduler timezone e2e",
        "priority": 3,
        "status": "not_started",
        "completed": False,
        "due_date": due_date,
        "thumbnail_url": None,
        "is_vital": False,
        "checklist_data": [],
    }

    response = requests.post(
        f"{BACKEND_URL}/api/v1/todos/",
        json=payload,
        cookies={
            "access_token": cookies["access_token"],
            "csrf_token": cookies.get("csrf_token", ""),
        },
        headers={
            "X-CSRF-Token": cookies.get("csrf_token", ""),
        },
        timeout=10,
    )
    if response.status_code not in (200, 201):
        raise RuntimeError(f"Create todo failed: {response.status_code} - {response.text}")

    todo = response.json()
    return todo.get("id")


def _get_unread_count(cookies: dict[str, str]) -> int:
    response = requests.get(
        f"{BACKEND_URL}/api/v1/notifications/unread-count",
        cookies={"access_token": cookies["access_token"]},
        timeout=10,
    )
    if response.status_code != 200:
        raise RuntimeError(f"Unread count failed: {response.status_code} - {response.text}")
    return int(response.json().get("unread_count", 0))


async def main() -> None:
    print("🔍 Running E2E Task23 - Scheduler timezone/window logic...")

    if not _wait_service_ready(DASHBOARD_URL):
        raise RuntimeError(f"Frontend is not ready at {DASHBOARD_URL}")
    if not _wait_service_ready(f"{BACKEND_URL}/health"):
        raise RuntimeError(f"Backend is not ready at {BACKEND_URL}/health")

    username, cookies = _register_and_login()
    todo_id = _create_due_soon_todo(cookies)

    before = _get_unread_count(cookies)

    # Trigger scheduler check manually in test context.
    await check_due_todos()
    after_first = _get_unread_count(cookies)

    # Run one more time to verify no duplicate notification for same due window.
    await check_due_todos()
    after_second = _get_unread_count(cookies)

    if after_first <= before:
        raise RuntimeError(
            f"Scheduler did not create reminder notification. before={before}, after_first={after_first}"
        )

    if after_second != after_first:
        raise RuntimeError(
            f"Duplicate reminder detected. after_first={after_first}, after_second={after_second}"
        )

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            cookie_items = [
                {
                    "name": "access_token",
                    "value": cookies["access_token"],
                    "domain": "localhost",
                    "path": "/",
                    "sameSite": "Lax",
                }
            ]
            if cookies.get("csrf_token"):
                cookie_items.append(
                    {
                        "name": "csrf_token",
                        "value": cookies["csrf_token"],
                        "domain": "localhost",
                        "path": "/",
                        "sameSite": "Lax",
                    }
                )

            await context.add_cookies(cookie_items)
            await page.goto(DASHBOARD_URL, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_url("**/dashboard**|**/login**", timeout=30000)

            if "/login" in page.url:
                raise RuntimeError("Cookie auth failed in browser context (redirected to /login).")

            # Open notifications popover and verify reminder content appears.
            bell_button = page.locator("button:has(svg.lucide-bell)").first
            await bell_button.wait_for(state="visible", timeout=15000)
            await bell_button.click()
            await page.get_by_text("Todo sắp đến hạn", exact=False).first.wait_for(state="visible", timeout=30000)

            print("\n✅ E2E PASSED")
            print(f"- User: {username}")
            print(f"- Todo ID: {todo_id}")
            print(f"- Unread before: {before}")
            print(f"- Unread after first run: {after_first}")
            print(f"- Unread after second run: {after_second}")
        finally:
            await context.close()
            await browser.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as exc:
        print(f"\n❌ E2E FAILED: {exc}")
        sys.exit(1)
