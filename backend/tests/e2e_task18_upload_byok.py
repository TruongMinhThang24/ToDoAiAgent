import asyncio
import os
import random
import string
import sys
import tempfile
from pathlib import Path

import requests
from playwright.async_api import async_playwright


FRONTEND_URL = os.getenv("E2E_BASE_URL", "http://localhost:3000")
BACKEND_URL = os.getenv("E2E_BACKEND_URL", "http://localhost:8000")
CHAT_URL = f"{FRONTEND_URL}/chat"
UPLOAD_ENDPOINT = "/api/v1/chat/knowledge/upload"
GEMINI_KEY_STORAGE = "todo_gemini_api_key"
RUNTIME_GEMINI_KEY = os.getenv("E2E_GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")


def _random_suffix(length: int = 8) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


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


def _create_and_login_user() -> dict[str, str]:
    username = f"e2e_t18_{_random_suffix()}"
    password = "admin12345"

    register_payload = {
        "username": username,
        "email": f"{username}@example.com",
        "first_name": "E2E",
        "last_name": "Task18",
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
    print("🤖 Task18 E2E: upload file + BYOK header propagation")

    if not RUNTIME_GEMINI_KEY:
        raise RuntimeError(
            "Missing runtime Gemini key. Set E2E_GEMINI_API_KEY (or GEMINI_API_KEY) before running this test."
        )

    if not await _wait_service_ready(f"{BACKEND_URL}/health"):
        raise RuntimeError("Backend not ready")
    if not await _wait_service_ready(CHAT_URL):
        raise RuntimeError("Frontend not ready")

    session = _create_and_login_user()

    upload_content = f"Task18 upload content {_random_suffix(6)}"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as tmp:
        tmp.write(upload_content)
        upload_path = Path(tmp.name)

    upload_headers: dict[str, str] = {}
    upload_status: int | None = None

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()

        await context.add_init_script(
            """({ key, value }) => {
                window.localStorage.setItem(key, value);
            }""",
            {"key": GEMINI_KEY_STORAGE, "value": RUNTIME_GEMINI_KEY},
        )

        page = await context.new_page()

        def _handle_request(request):
            nonlocal upload_headers
            if request.method == "POST" and UPLOAD_ENDPOINT in request.url:
                upload_headers = request.headers

        def _handle_response(response):
            nonlocal upload_status
            if response.request.method == "POST" and UPLOAD_ENDPOINT in response.url:
                upload_status = response.status

        page.on("request", _handle_request)
        page.on("response", _handle_response)

        try:
            cookies = [
                {
                    "name": "access_token",
                    "value": session["access_token"],
                    "url": FRONTEND_URL,
                    "sameSite": "Lax",
                }
            ]
            if session["csrf_token"]:
                cookies.append(
                    {
                        "name": "csrf_token",
                        "value": session["csrf_token"],
                        "url": FRONTEND_URL,
                        "sameSite": "Lax",
                    }
                )
            await context.add_cookies(cookies)

            await page.goto(CHAT_URL, wait_until="domcontentloaded", timeout=30000)
            await page.get_by_placeholder("Type your message...").wait_for(state="visible", timeout=15000)

            file_input = page.locator("input[type='file']")
            await file_input.set_input_files(str(upload_path))

            await page.get_by_role("button", name="Send").click()
            await page.get_by_text("Đã tải tài liệu", exact=False).first.wait_for(state="visible", timeout=45000)

            if upload_status not in (200, 201):
                raise RuntimeError(f"Upload response status is unexpected: {upload_status}")

            sent_key = upload_headers.get("x-gemini-api-key") or upload_headers.get("X-Gemini-API-Key")
            if sent_key != RUNTIME_GEMINI_KEY:
                raise RuntimeError("Upload request is missing X-Gemini-API-Key header or value mismatch.")

            print("✅ Task18 E2E passed")
            print(f"- Upload status: {upload_status}")
            print("- X-Gemini-API-Key header propagated correctly")
        finally:
            await context.close()
            await browser.close()
            try:
                upload_path.unlink(missing_ok=True)
            except OSError:
                pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as exc:
        print(f"❌ Task18 E2E failed: {exc}")
        sys.exit(1)
