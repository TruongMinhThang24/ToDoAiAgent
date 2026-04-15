import asyncio
import os
import random
import string
import sys

import requests
from playwright.async_api import async_playwright


FRONTEND_URL = os.getenv('E2E_BASE_URL', 'http://localhost:3000')
BACKEND_URL = os.getenv('E2E_BACKEND_URL', 'http://localhost:8000')
VOICE_ROOM_URL = f'{FRONTEND_URL}/voice-room'
GEMINI_KEY_STORAGE = 'todo_gemini_api_key'


def _random_suffix(length: int = 8) -> str:
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


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
    username = f'e2e_t20_{_random_suffix()}'
    password = 'admin12345'

    register_payload = {
        'username': username,
        'email': f'{username}@example.com',
        'first_name': 'E2E',
        'last_name': 'Task20',
        'password': password,
        'phone_number': '0123456789',
    }
    register_response = requests.post(f'{BACKEND_URL}/auth/register', json=register_payload, timeout=10)
    if register_response.status_code not in (200, 201):
        raise RuntimeError(f'Register failed: {register_response.status_code} - {register_response.text}')

    login_response = requests.post(
        f'{BACKEND_URL}/auth/token',
        data={'username': username, 'password': password},
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        timeout=10,
    )
    if login_response.status_code != 200:
        raise RuntimeError(f'Login failed: {login_response.status_code} - {login_response.text}')

    access_token = login_response.cookies.get('access_token')
    csrf_token = login_response.cookies.get('csrf_token')
    if not access_token:
        raise RuntimeError('Missing access_token cookie after login')

    return {
        'access_token': access_token,
        'csrf_token': csrf_token or '',
    }


async def main() -> None:
    print('🤖 Task20 E2E: voice room frontend flow')

    if not await _wait_service_ready(f'{BACKEND_URL}/health'):
        raise RuntimeError('Backend not ready')
    if not await _wait_service_ready(VOICE_ROOM_URL):
        raise RuntimeError('Frontend not ready')

    session = _create_and_login_user()
    runtime_gemini_key = f'test-gemini-key-{_random_suffix(12)}'
    captured_request: dict[str, str] = {}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()

        await context.add_init_script(
            """({ key, value }) => {
                window.localStorage.setItem(key, value);
                if (!navigator.mediaDevices) {
                  navigator.mediaDevices = {};
                }

                navigator.mediaDevices.getUserMedia = async () => ({
                  getTracks: () => [{ stop: () => {} }],
                });

                class FakeMediaRecorder {
                  constructor(stream, options = {}) {
                    this.stream = stream;
                    this.mimeType = options.mimeType || 'audio/webm';
                    this.state = 'inactive';
                    this.ondataavailable = null;
                    this.onstop = null;
                  }

                  start() {
                    this.state = 'recording';
                  }

                  stop() {
                    this.state = 'inactive';
                    if (this.ondataavailable) {
                      this.ondataavailable({ data: new Blob(['voice-room-audio'], { type: this.mimeType }) });
                    }
                    if (this.onstop) {
                      this.onstop();
                    }
                  }

                  static isTypeSupported() {
                    return true;
                  }
                }

                window.MediaRecorder = FakeMediaRecorder;
                window.Audio.prototype.play = function play() {
                  setTimeout(() => this.dispatchEvent(new Event('ended')), 0);
                  return Promise.resolve();
                };
            }""",
            {'key': GEMINI_KEY_STORAGE, 'value': runtime_gemini_key},
        )

        page = await context.new_page()

        async def handle_voice_route(route):
            request = route.request
            captured_request['method'] = request.method
            captured_request['url'] = request.url
            captured_request['content_type'] = request.headers.get('content-type', '')
            captured_request['gemini_key'] = request.headers.get('x-gemini-api-key', '')

            raw_body = b''
            if hasattr(request, 'post_data_buffer'):
                try:
                    raw_body = request.post_data_buffer() or b''
                except Exception:
                    raw_body = b''
            if not raw_body:
                post_data = request.post_data() or ''
                raw_body = post_data.encode('utf-8', errors='ignore')

            captured_request['body_preview'] = raw_body.decode('utf-8', errors='ignore')

            if request.method != 'POST':
                raise RuntimeError(f'Unexpected method: {request.method}')
            if '/api/v1/chat/voice' not in request.url:
                raise RuntimeError(f'Unexpected URL: {request.url}')
            if runtime_gemini_key not in captured_request['gemini_key']:
                raise RuntimeError('X-Gemini-API-Key header is missing or wrong.')
            if 'multipart/form-data' not in captured_request['content_type']:
                raise RuntimeError('Voice request must use multipart/form-data.')
            if 'name="audio"' not in captured_request['body_preview']:
                raise RuntimeError('Voice request body is missing audio form field.')

            await route.fulfill(
                status=200,
                content_type='audio/mpeg',
                body=b'FAKE-VOICE-RESPONSE',
            )

        await page.route('**/api/v1/chat/voice', handle_voice_route)

        try:
            cookies = [
                {
                    'name': 'access_token',
                    'value': session['access_token'],
                    'url': FRONTEND_URL,
                    'sameSite': 'Lax',
                }
            ]
            if session['csrf_token']:
                cookies.append(
                    {
                        'name': 'csrf_token',
                        'value': session['csrf_token'],
                        'url': FRONTEND_URL,
                        'sameSite': 'Lax',
                    }
                )

            await context.add_cookies(cookies)

            await page.goto(VOICE_ROOM_URL, wait_until='domcontentloaded', timeout=30000)
            await page.wait_for_url('**/voice-room**', timeout=30000)

            record_button = page.get_by_role('button', name='Bắt đầu ghi âm')
            await record_button.wait_for(state='visible', timeout=15000)

            await record_button.click()
            await page.get_by_text('Đang nghe...', exact=False).wait_for(state='visible', timeout=15000)

            await page.get_by_role('button', name='Dừng ghi âm').click()
            await page.get_by_text('Đang xử lý...', exact=False).wait_for(state='visible', timeout=15000)
            await page.get_by_text('AI đang nói...', exact=False).wait_for(state='visible', timeout=15000)
            await page.get_by_text('Sẵn sàng nhận giọng nói.', exact=False).wait_for(state='visible', timeout=15000)

            print('\n✅ KẾT QUẢ TEST E2E:')
            print(f"- URL hiện tại: {page.url}")
            print(f"- Voice request URL: {captured_request.get('url')}")
            print(f"- Voice request header x-gemini-api-key: {captured_request.get('gemini_key')}")
            print(f"- Voice request content-type: {captured_request.get('content_type')}")
            print(f"- Voice request body preview: {captured_request.get('body_preview', '')[:120]}")
        finally:
            await context.close()
            await browser.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as exc:
        print(f'\n❌ E2E FAILED: {exc}')
        sys.exit(1)