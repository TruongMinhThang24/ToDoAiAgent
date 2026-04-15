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


def _create_and_login_user() -> tuple[str, dict[str, str]]:
    username = f"e2e_task22_{_random_suffix()}"
    payload = {
        "username": username,
        "email": f"{username}@example.com",
        "first_name": "E2E",
        "last_name": "Task22",
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


async def main() -> None:
    print("🔍 Running E2E Task22 - Due datetime picker + payload sync...")

    if not _wait_service_ready(DASHBOARD_URL):
        raise RuntimeError(f"Frontend is not ready at {DASHBOARD_URL}")

    if not _wait_service_ready(f"{BACKEND_URL}/health"):
        raise RuntimeError(f"Backend is not ready at {BACKEND_URL}/health")

    username, cookies = _create_and_login_user()

    task_title = f"E2E-DUEDT-{_random_suffix(6).upper()}"
    task_desc = "Created by Playwright e2e_task22_due_datetime.py"
    captured_body = {}

    # past value để verify cảnh báo nhẹ
    past_due_local = "2000-01-01T08:30"
    # future value để submit thật
    future_due_local = "2030-12-31T21:45"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        def _capture_request(request):
            if request.method == "POST" and "/api/v1/todos/" in request.url:
                try:
                    captured_body["json"] = request.post_data_json
                except Exception:
                    captured_body["json"] = None
                captured_body["raw"] = request.post_data or ""

        page.on("request", _capture_request)

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

            # Nếu cookie không được nhận, app sẽ redirect về /login.
            await page.wait_for_url("**/dashboard**|**/login**", timeout=30000)
            if "/login" in page.url:
                raise RuntimeError(
                    "Cookie auth chưa được nhận trong browser context (đang ở /login). "
                    "Hãy kiểm tra backend /auth/token và domain localhost."
                )

            add_task_button = page.get_by_role("button", name="ADD TASK")
            await add_task_button.wait_for(state="visible", timeout=15000)
            await add_task_button.click()
            await page.get_by_placeholder("Enter task title...").wait_for(state="visible", timeout=15000)

            await page.get_by_placeholder("Enter task title...").fill(task_title)
            await page.get_by_placeholder("Start writing here...").fill(task_desc)

            due_input = page.locator("input[type='datetime-local']").first
            await due_input.fill(past_due_local)
            await page.get_by_text("Hạn chót đang ở quá khứ", exact=False).wait_for(state="visible", timeout=10000)

            await due_input.fill(future_due_local)
            await page.get_by_text("Hạn chót đang ở quá khứ", exact=False).wait_for(state="hidden", timeout=10000)

            await page.get_by_role("button", name="Done").click()

            await page.get_by_placeholder("Enter task title...").wait_for(state="hidden", timeout=15000)
            await page.locator("h4", has_text=task_title).first.wait_for(state="visible", timeout=15000)

            if not captured_body.get("raw"):
                raise RuntimeError("Không bắt được request POST /api/v1/todos/ để kiểm tra payload.")

            payload_text = captured_body["raw"]
            if '"due_date":' not in payload_text:
                raise RuntimeError("Payload thiếu trường due_date.")
            if "2030-12-31" not in payload_text:
                raise RuntimeError("Payload due_date không đồng bộ với datetime đã nhập.")

            print("\n✅ E2E PASSED")
            print(f"- User: {username}")
            print(f"- Task title: {task_title}")
            print(f"- Due input: {future_due_local}")
            print(f"- Payload preview: {payload_text[:180]}")

        finally:
            await context.close()
            await browser.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as exc:
        print(f"\n❌ E2E FAILED: {exc}")
        sys.exit(1)
