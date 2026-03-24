import asyncio
import os
import random
import string
import sys
import time
from playwright.async_api import async_playwright
import requests


BASE_URL = os.getenv("E2E_BASE_URL", "http://localhost:3000")
LOGIN_URL = f"{BASE_URL}/login"
TODOS_URL = f"{BASE_URL}/todos"
BACKEND_URL = os.getenv("E2E_BACKEND_URL", "http://localhost:8000")
USERNAME = os.getenv("E2E_USERNAME")
PASSWORD = os.getenv("E2E_PASSWORD", "admin12345")
SEARCH_TEXT = os.getenv("E2E_SEARCH_TEXT", "họp")


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
    return f"e2e_{suffix}"


def _random_todo_title() -> str:
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"E2E-TODO-{suffix}"


def _ensure_test_account() -> tuple[str, str]:
    # Nếu user truyền sẵn credentials thì dùng trực tiếp.
    if USERNAME:
        return USERNAME, PASSWORD

    username = _random_user()
    password = PASSWORD
    payload = {
        "username": username,
        "email": f"{username}@example.com",
        "first_name": "E2E",
        "last_name": "Tester",
        "password": password,
        "phone_number": "0123456789",
    }

    response = requests.post(f"{BACKEND_URL}/auth/register", json=payload, timeout=10)
    if response.status_code not in (200, 201):
        raise RuntimeError(
            f"Không tạo được tài khoản test. status={response.status_code}, body={response.text}"
        )

    return username, password


def _login_and_get_cookies(username: str, password: str) -> dict[str, str]:
    form_data = {
        "username": username,
        "password": password,
    }
    response = requests.post(
        f"{BACKEND_URL}/auth/token",
        data=form_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10,
    )
    if response.status_code != 200:
        raise RuntimeError(
            f"Login API thất bại. status={response.status_code}, body={response.text}"
        )

    access_token = response.cookies.get("access_token")
    csrf_token = response.cookies.get("csrf_token")
    if not access_token:
        raise RuntimeError("Không nhận được cookie access_token từ backend /auth/token")

    return {
        "access_token": access_token,
        "csrf_token": csrf_token or "",
    }


async def main():
    print("🤖 Đang khởi động E2E Tester (Playwright)...")

    # 0) Kiểm tra frontend/backend đã chạy chưa
    if not _wait_service_ready(LOGIN_URL):
        raise RuntimeError(
            f"Frontend chưa sẵn sàng tại {LOGIN_URL}. Hãy chạy frontend trước."
        )

    if not _wait_service_ready(f"{BACKEND_URL}/health"):
        raise RuntimeError(
            f"Backend chưa sẵn sàng tại {BACKEND_URL}. Hãy chạy backend (uvicorn src.main:app --reload)."
        )

    username, password = _ensure_test_account()
    print(f"ℹ️ Dùng tài khoản test: {username}")
    cookies = _login_and_get_cookies(username, password)
    created_todo_title = os.getenv("E2E_TODO_TITLE", _random_todo_title())

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # Set auth cookies vào browser context để vào thẳng /todos (ổn định hơn auto-login UI)
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

            # Vào trang todos và chờ UI sẵn sàng
            await page.goto(TODOS_URL, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_url("**/todos**", timeout=30000)

            # A) Tạo mới todo test qua UI
            await page.get_by_role("button", name="add task").click()
            await page.get_by_placeholder("Nhập tên công việc…").wait_for(state="visible", timeout=15000)

            await page.get_by_placeholder("Nhập tên công việc…").fill(created_todo_title)
            await page.get_by_placeholder("Mô tả công việc…").fill(f"Auto created by E2E: {created_todo_title}")
            await page.locator("form button[type='submit']").click()

            # Sau khi add thành công, UI quay về inbox
            search_input = page.get_by_placeholder("Search by title or description...")
            await search_input.wait_for(state="visible", timeout=15000)

            # B) Tìm đúng todo vừa tạo
            await search_input.fill(created_todo_title)

            # Chờ debounce/filter render
            await page.wait_for_timeout(2000)

            # Kiểm tra title vừa tạo hiển thị trong danh sách
            created_todo_locator = page.locator("span", has_text=created_todo_title)
            await created_todo_locator.first.wait_for(state="visible", timeout=15000)
            exact_match_count = await created_todo_locator.count()
            if exact_match_count != 1:
                raise RuntimeError(
                    f"Kỳ vọng tìm đúng 1 todo '{created_todo_title}', nhưng thấy {exact_match_count}."
                )

            # Đếm số item đang hiển thị
            visible_badges = page.locator("span:has-text('TODO'), span:has-text('DONE')")
            total_visible = await visible_badges.count()

            print("\n✅ KẾT QUẢ TEST E2E:")
            print(f"- URL hiện tại: {page.url}")
            print(f"- Todo vừa tạo: '{created_todo_title}'")
            print(f"- Search text: '{created_todo_title}'")
            print(f"- Số kết quả khớp đúng title: {exact_match_count}")
            print(f"- Số todo item đang hiển thị: {total_visible}")

        finally:
            await context.close()
            await browser.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as exc:
        print(f"\n❌ E2E FAILED: {exc}")
        sys.exit(1)