import random
import string
import sys
from pathlib import Path

from fastapi.testclient import TestClient

# Ensure `backend/src` is importable when running `pytest` from backend root.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / 'src'
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from main import app
from todo_backend.domain.entities.models import Notification
from todo_backend.infrastructure.database.database import sessionLocal


def _random_suffix(length: int = 8) -> str:
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


def _register_and_login(client: TestClient, *, username_prefix: str = 'notif') -> dict:
    username = f'{username_prefix}_{_random_suffix()}'
    password = 'admin12345'

    register_response = client.post(
        '/auth/register',
        json={
            'username': username,
            'email': f'{username}@example.com',
            'first_name': 'Notif',
            'last_name': 'Tester',
            'password': password,
            'phone_number': '0123456789',
        },
    )
    assert register_response.status_code == 201, register_response.text

    login_response = client.post(
        '/auth/token',
        data={'username': username, 'password': password},
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
    )
    assert login_response.status_code == 200, login_response.text

    me_response = client.get('/auth/me')
    assert me_response.status_code == 200, me_response.text

    return {
        'user_id': me_response.json()['id'],
        'csrf_token': client.cookies.get('csrf_token') or '',
    }


def test_notifications_list_mark_and_ownership() -> None:
    with TestClient(app) as client_user_1, TestClient(app) as client_user_2:
        user1 = _register_and_login(client_user_1, username_prefix='notif_u1')
        user2 = _register_and_login(client_user_2, username_prefix='notif_u2')

        db = sessionLocal()
        try:
            n1 = Notification(
                user_id=user1['user_id'],
                type='todo_due_soon',
                title='Due soon #1',
                message='Todo 1 is due soon',
                metadata_json={'todo_id': 1001},
                is_read=False,
            )
            n2 = Notification(
                user_id=user1['user_id'],
                type='todo_due_soon',
                title='Due soon #2',
                message='Todo 2 is due soon',
                metadata_json={'todo_id': 1002},
                is_read=False,
            )
            n_other = Notification(
                user_id=user2['user_id'],
                type='todo_due_soon',
                title='Other user',
                message='Other user notification',
                metadata_json={'todo_id': 2001},
                is_read=False,
            )
            db.add_all([n1, n2, n_other])
            db.commit()
            db.refresh(n1)
            db.refresh(n2)
            db.refresh(n_other)
        finally:
            db.close()

        list_response = client_user_1.get('/api/v1/notifications?limit=20&offset=0')
        assert list_response.status_code == 200, list_response.text
        payload = list_response.json()
        assert payload['total'] >= 2
        assert all(item['user_id'] == user1['user_id'] for item in payload['items'])

        unread_response = client_user_1.get('/api/v1/notifications/unread-count')
        assert unread_response.status_code == 200, unread_response.text
        assert unread_response.json()['unread_count'] >= 2

        csrf_headers = {'X-CSRF-Token': user1['csrf_token']}

        forbidden_mark = client_user_1.patch(
            f"/api/v1/notifications/{n_other.id}/read",
            headers=csrf_headers,
        )
        assert forbidden_mark.status_code == 404, forbidden_mark.text

        mark_one = client_user_1.patch(
            f"/api/v1/notifications/{n1.id}/read",
            headers=csrf_headers,
        )
        assert mark_one.status_code == 200, mark_one.text
        assert mark_one.json()['is_read'] is True

        mark_all_first = client_user_1.patch('/api/v1/notifications/read-all', headers=csrf_headers)
        assert mark_all_first.status_code == 200, mark_all_first.text
        assert mark_all_first.json()['unread_count'] == 0

        mark_all_second = client_user_1.patch('/api/v1/notifications/read-all', headers=csrf_headers)
        assert mark_all_second.status_code == 200, mark_all_second.text
        assert mark_all_second.json()['marked_count'] == 0
