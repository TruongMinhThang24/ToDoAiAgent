# backend/src/todo_backend/api/routers/notifications.py
import logging

from fastapi import (APIRouter, WebSocket, WebSocketDisconnect,
                     status, HTTPException)

# Import singleton manager
from todo_backend.infrastructure.notification.websocket_manager import \
    websocket_manager

# --- THAY ĐỔI QUAN TRỌNG ---
# 1. Import hàm validate mới và db_dependency
from .auth import validate_token_and_get_user, db_dependency
# ---
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    db: db_dependency  # 2. Inject db_dependency
):
    """
    Endpoint WebSocket.
    Xác thực thủ công token từ header.
    """
    
    token = None
    user = None
    try:
        # 3. Lấy token thủ công từ header
        auth_header = websocket.headers.get("Authorization")
        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == "bearer":
                token = parts[1]

        if not token:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Missing token")
            return

        # 4. Gọi hàm validate_token_and_get_user
        user = await validate_token_and_get_user(token, db)
        
        if user is None:
             await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="User not found")
             return

    except HTTPException: # Bắt lỗi 401
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Could not validate credentials")
        return
    except Exception as e:
        logger.error(f"WebSocket auth error: {e}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Authentication error")
        return

    # --- Kết thúc xác thực ---

    user_id = user["id"]
    await websocket_manager.connect(user_id, websocket)
    
    try:
        while True:
            # Giữ kết nối mở
            await websocket.receive_text() 
    except WebSocketDisconnect:
        websocket_manager.disconnect(user_id, websocket)
    except Exception as e:
        logger.error(f"WebSocket Error for user {user_id}: {e}")
        websocket_manager.disconnect(user_id, websocket)