import asyncio
import os
import random
import string
import sys
import time

import requests
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright


FRONTEND_URL = os.getenv("E2E_BASE_URL", "http://localhost:3000")
BACKEND_URL = os.getenv("E2E_BACKEND_URL", "http://localhost:8000")
DASHBOARD_URL = f"{FRONTEND_URL}/dashboard"
PASSWORD = os.getenv("E2E_PASSWORD", "admin12345")
USERNAME = os.getenv("E2E_USERNAME")


def _random_suffix(length: int = 8) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def _random_title() -> str:
    return f"TASK07-{_random_suffix(6).upper()}"


async def _wait_service_ready(url: str, timeout_seconds: int = 30) -> None:
    deadline = time.monotonic() + timeout_seconds
    last_error = ""

    while time.monotonic() < deadline:
        try:
            response = requests.get(url, timeout=3)
            if 200 <= response.status_code < 500:
                return
            last_error = f"status={response.status_code}"
        except requests.RequestException as exc:
            last_error = str(exc)

        await asyncio.sleep(0.5)

    raise RuntimeError(f"Service not ready: {url}. Last error: {last_error}")


def _ensure_test_account() -> tuple[str, str]:
    if USERNAME:
        return USERNAME, PASSWORD

    username = f"e2e_task07_{_random_suffix()}"
    payload = {
        "username": username,
        "email": f"{username}@example.com",
        "first_name": "E2E",
        "last_name": "Task07",
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


async def _create_task_with_retry(page, title: str, description: str, retries: int = 2) -> None:
    last_error = None

    for attempt in range(1, retries + 1):
        try:
            await page.get_by_role("button", name="ADD TASK").click(timeout=15000)
            await page.get_by_placeholder("Enter task title...").wait_for(state="visible", timeout=15000)

            await page.get_by_placeholder("Enter task title...").fill(title)
            await page.get_by_placeholder("Start writing here...").fill(description)
            await page.locator("input[type='date']").fill("2026-12-31")

            await page.get_by_role("button", name="Done").click(timeout=15000)

            # Modal chỉ đóng khi API thành công.
            await page.get_by_placeholder("Enter task title...").wait_for(state="hidden", timeout=15000)
            return
        except PlaywrightTimeoutError as exc:
            last_error = exc
            # Nếu lần này fail, cố đóng modal và thử lại 1 lần.
            if attempt < retries:
                go_back_btn = page.get_by_role("button", name="Go Back")
                if await go_back_btn.count() > 0:
                    await go_back_btn.click()
                    await go_back_btn.wait_for(state="hidden", timeout=10000)
                continue

    raise RuntimeError(f"Cannot create task from UI after {retries} attempts: {last_error}")


async def main() -> None:
    print("🔎 Running E2E Task07 - Contract-first Add Task flow...")

    await _wait_service_ready(f"{FRONTEND_URL}/login")
    await _wait_service_ready(f"{BACKEND_URL}/health")

    username, password = _ensure_test_account()
    cookies = _login_and_get_cookies(username, password)

    task_title = _random_title()
    task_desc = f"Created by e2e_task07_add_task_contract.py - {task_title}"

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            cookie_items = [
                {
                    "name": "access_token",
                    "value": cookies["access_token"],
                    "url": FRONTEND_URL,
                    "sameSite": "Lax",
                }
            ]
            if cookies.get("csrf_token"):
                cookie_items.append(
                    {
                        "name": "csrf_token",
                        "value": cookies["csrf_token"],
                        "url": FRONTEND_URL,
                        "sameSite": "Lax",
                    }
                )

            await context.add_cookies(cookie_items)

            await page.goto(DASHBOARD_URL, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_url("**/dashboard**", timeout=30000)

            await _create_task_with_retry(page, task_title, task_desc, retries=2)

            # Assert task xuất hiện trên dashboard/list.
            await page.locator("h4", has_text=task_title).first.wait_for(state="visible", timeout=20000)

            print("✅ E2E Task07 passed")
            print(f"- user: {username}")
            print(f"- task title: {task_title}")
            print(f"- page: {page.url}")

        finally:
            await context.close()
            await browser.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as exc:
        print(f"\n❌ E2E Task07 FAILED: {exc}")
        sys.exit(1)
