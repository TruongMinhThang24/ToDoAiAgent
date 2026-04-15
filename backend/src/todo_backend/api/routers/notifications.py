import logging
from typing import Annotated, Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    WebSocket,
    WebSocketDisconnect,
    status,
)

from todo_backend.api.schemas.notification_schema import (
    MarkAllReadResponse,
    NotificationItemResponse,
    NotificationListResponse,
    UnreadCountResponse,
)
from todo_backend.app.usecases.notification_center import NotificationCenterUseCases
from todo_backend.infrastructure.notification.websocket_manager import websocket_manager
from todo_backend.infrastructure.repositories.notification_center_repository_impl import (
    NotificationCenterRepositoryImpl,
)

from .auth import db_dependency, get_current_user, validate_token_and_get_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/notifications", tags=["notifications"])

user_dependency = Annotated[dict, Depends(get_current_user)]


def _extract_ws_token(websocket: WebSocket) -> str | None:
    """
    Ưu tiên đọc JWT từ HttpOnly cookie (flow auth hiện tại của hệ thống).
    Fallback sang Authorization header để giữ tương thích ngược.
    """
    token_from_cookie = websocket.cookies.get("access_token")
    if token_from_cookie:
        return token_from_cookie

    auth_header = websocket.headers.get("Authorization")
    if not auth_header:
        return None

    parts = auth_header.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]

    return None


@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    db: db_dependency,
    user: user_dependency,
    is_read: Optional[bool] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    service = NotificationCenterUseCases(NotificationCenterRepositoryImpl(db))
    items, total = service.list_notifications(
        user_id=user["id"],
        is_read=is_read,
        limit=limit,
        offset=offset,
    )
    return {
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/unread-count", response_model=UnreadCountResponse)
async def unread_count(
    db: db_dependency,
    user: user_dependency,
):
    service = NotificationCenterUseCases(NotificationCenterRepositoryImpl(db))
    return {"unread_count": service.unread_count(user_id=user["id"])}


@router.patch("/{notification_id}/read", response_model=NotificationItemResponse)
async def mark_read(
    notification_id: int,
    db: db_dependency,
    user: user_dependency,
):
    service = NotificationCenterUseCases(NotificationCenterRepositoryImpl(db))
    item = service.mark_read(user_id=user["id"], notification_id=notification_id)
    if not item:
        raise HTTPException(status_code=404, detail="Notification not found")

    unread_count_value = service.unread_count(user_id=user["id"])
    await websocket_manager.send_json_to_user(
        user["id"],
        {
            "event": "notification.read",
            "notification": item,
            "unread_count": unread_count_value,
        },
    )
    return item


@router.patch("/read-all", response_model=MarkAllReadResponse)
async def mark_all_read(
    db: db_dependency,
    user: user_dependency,
):
    service = NotificationCenterUseCases(NotificationCenterRepositoryImpl(db))
    marked_count = service.mark_all_read(user_id=user["id"])
    unread_count_value = service.unread_count(user_id=user["id"])

    await websocket_manager.send_json_to_user(
        user["id"],
        {
            "event": "notification.read_all",
            "notification": None,
            "unread_count": unread_count_value,
        },
    )

    return {
        "marked_count": marked_count,
        "unread_count": unread_count_value,
    }


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    db: db_dependency,
):
    """
    Endpoint WebSocket.
    Xác thực token từ cookie hoặc Authorization header.
    """
    try:
        token = _extract_ws_token(websocket)

        if not token:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Missing token")
            return

        user = await validate_token_and_get_user(token, db)
        if user is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="User not found")
            return
    except HTTPException:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Could not validate credentials")
        return
    except Exception as exc:
        logger.error("WebSocket auth error: %s", exc)
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Authentication error")
        return

    user_id = user["id"]
    await websocket_manager.connect(user_id, websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_manager.disconnect(user_id, websocket)
    except Exception as exc:
        logger.error("WebSocket Error for user %s: %s", user_id, exc)
        websocket_manager.disconnect(user_id, websocket)