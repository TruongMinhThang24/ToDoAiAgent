import asyncio
import os
import random
import string
import sys
from datetime import UTC, datetime, timedelta

import requests
from playwright.async_api import async_playwright


FRONTEND_URL = os.getenv('E2E_BASE_URL', 'http://localhost:3000')
BACKEND_URL = os.getenv('E2E_BACKEND_URL', 'http://localhost:8000')
DASHBOARD_URL = f'{FRONTEND_URL}/dashboard'


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
    username = f'e2e_t21_{_random_suffix()}'
    password = 'admin12345'

    register_payload = {
        'username': username,
        'email': f'{username}@example.com',
        'first_name': 'E2E',
        'last_name': 'Task21',
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


def _create_due_soon_todo(csrf_token: str) -> None:
    due_date = (datetime.now(UTC) + timedelta(minutes=4)).replace(microsecond=0)
    payload = {
        'title': f'E2E Notification Todo {_random_suffix(6)}',
        'description': 'Todo created for scheduler reminder',
        'priority': 3,
        'completed': False,
        'due_date': due_date.isoformat(),
        'status': 'not_started',
        'thumbnail_url': None,
        'is_vital': False,
        'checklist_data': None,
    }

    response = requests.post(
        f'{BACKEND_URL}/api/v1/todos/',
        json=payload,
        cookies={'access_token': SESSION['access_token'], 'csrf_token': csrf_token},
        headers={'X-CSRF-Token': csrf_token},
        timeout=10,
    )
    if response.status_code not in (200, 201):
        raise RuntimeError(f'Create due-soon todo failed: {response.status_code} - {response.text}')


SESSION: dict[str, str] = {}


async def _wait_unread_count(timeout_seconds: int = 120) -> int:
    deadline = asyncio.get_running_loop().time() + timeout_seconds
    while asyncio.get_running_loop().time() < deadline:
      try:
          response = requests.get(
              f'{BACKEND_URL}/api/v1/notifications/unread-count',
              cookies={'access_token': SESSION['access_token']},
              timeout=5,
          )
          if response.status_code == 200:
              unread = int(response.json().get('unread_count') or 0)
              if unread > 0:
                  return unread
      except Exception:
          pass
      await asyncio.sleep(2)
    return 0


async def main() -> None:
    print('🤖 Task21 E2E: notifications center realtime flow')

    if not await _wait_service_ready(f'{BACKEND_URL}/health'):
        raise RuntimeError('Backend not ready')
    if not await _wait_service_ready(DASHBOARD_URL):
        raise RuntimeError('Frontend not ready')

    global SESSION
    SESSION = _create_and_login_user()
    _create_due_soon_todo(SESSION['csrf_token'])
    unread_count = await _wait_unread_count(timeout_seconds=120)
    if unread_count <= 0:
        raise RuntimeError('Scheduler did not create unread notification within timeout.')

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            cookies = [
                {
                    'name': 'access_token',
                    'value': SESSION['access_token'],
                    'url': FRONTEND_URL,
                    'sameSite': 'Lax',
                }
            ]
            if SESSION['csrf_token']:
                cookies.append(
                    {
                        'name': 'csrf_token',
                        'value': SESSION['csrf_token'],
                        'url': FRONTEND_URL,
                        'sameSite': 'Lax',
                    }
                )
            await context.add_cookies(cookies)

            await page.goto(DASHBOARD_URL, wait_until='domcontentloaded', timeout=30000)
            await page.wait_for_url('**/dashboard**', timeout=30000)

            bell_button = page.locator('button:has(svg.lucide-bell)').first
            await bell_button.wait_for(state='visible', timeout=15000)

            await page.wait_for_timeout(1500)

            await bell_button.click()
            await page.get_by_text('Notifications', exact=False).wait_for(state='visible', timeout=15000)
            await page.get_by_text('Todo sắp đến hạn', exact=False).first.wait_for(state='visible', timeout=90000)

            await page.get_by_role('button', name='Mark all read').click()
            await page.wait_for_function(
                """() => {
                    const badge = document.querySelector('button .bg-emerald-500');
                    return !badge;
                }""",
                timeout=20000,
            )

            print('\n✅ KẾT QUẢ TEST E2E:')
            print(f'- URL hiện tại: {page.url}')
            print('- Badge thông báo realtime đã xuất hiện và về 0 sau mark-all-read')
        finally:
            await context.close()
            await browser.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as exc:
        print(f'\n❌ E2E FAILED: {exc}')
        sys.exit(1)
