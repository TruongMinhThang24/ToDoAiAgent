import asyncio
import os
import random
import string
import sys
import time

import requests
from playwright.async_api import async_playwright

BASE_URL = os.getenv("E2E_BASE_URL", "http://localhost:3000")
BACKEND_URL = os.getenv("E2E_BACKEND_URL", "http://localhost:8000")
DASHBOARD_URL = f"{BASE_URL}/dashboard"
PASSWORD = os.getenv("E2E_PASSWORD", "admin12345")
USERNAME = os.getenv("E2E_USERNAME")


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


def _random_suffix(length: int = 8) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def _ensure_test_account() -> tuple[str, str]:
    if USERNAME:
        return USERNAME, PASSWORD

    username = f"e2e_task06_{_random_suffix()}"
    payload = {
        "username": username,
        "email": f"{username}@example.com",
        "first_name": "E2E",
        "last_name": "Task06",
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


async def main() -> None:
    print("🔍 Running E2E Task06 - Add Task API flow...")

    if not _wait_service_ready(DASHBOARD_URL):
        raise RuntimeError(f"Frontend is not ready at {DASHBOARD_URL}")

    if not _wait_service_ready(f"{BACKEND_URL}/health"):
        raise RuntimeError(f"Backend is not ready at {BACKEND_URL}/health")

    username, password = _ensure_test_account()
    cookies = _login_and_get_cookies(username, password)

    task_title = f"E2E-ADD-TASK-{_random_suffix(6).upper()}"
    task_desc = "Created by Playwright e2e_task06_add_task_api.py"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            cookie_items = [
                {
                    "name": "access_token",
                    "value": cookies["access_token"],
                    "url": BASE_URL,
                    "sameSite": "Lax",
                }
            ]
            if cookies.get("csrf_token"):
                cookie_items.append(
                    {
                        "name": "csrf_token",
                        "value": cookies["csrf_token"],
                        "url": BASE_URL,
                        "sameSite": "Lax",
                    }
                )

            await context.add_cookies(cookie_items)
            await page.goto(DASHBOARD_URL, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_url("**/dashboard**", timeout=30000)

            # Open add modal
            await page.get_by_role("button", name="ADD TASK").click()
            await page.get_by_placeholder("Enter task title...").wait_for(state="visible", timeout=15000)

            # Fill form
            await page.get_by_placeholder("Enter task title...").fill(task_title)
            await page.get_by_placeholder("Start writing here...").fill(task_desc)
            await page.locator("input[type='date']").fill("2026-12-31")

            # Submit
            await page.get_by_role("button", name="Done").click()

            # Verify modal closed and task appears on dashboard cards
            await page.get_by_placeholder("Enter task title...").wait_for(state="hidden", timeout=15000)
            await page.locator("h4", has_text=task_title).first.wait_for(state="visible", timeout=15000)

            print("\n✅ E2E PASSED")
            print(f"- User: {username}")
            print(f"- Created task title: {task_title}")
            print(f"- Dashboard URL: {page.url}")

        finally:
            await context.close()
            await browser.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as exc:
        print(f"\n❌ E2E FAILED: {exc}")
        sys.exit(1)
