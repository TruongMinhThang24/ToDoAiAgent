# backend/src/todo_backend/app/scheduler.py
import logging
from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session

from todo_backend.domain.entities.models import Todo
from todo_backend.infrastructure.database.database import sessionLocal

# --- (THAY ĐỔI) ---
# 1. Import UseCase và Singleton Manager
from todo_backend.app.usecases.notification import NotificationUseCases
from todo_backend.infrastructure.notification.websocket_manager import \
    websocket_manager

# --- (HẾT THAY ĐỔI) ---

# Thiết lập logger
logger = logging.getLogger(__name__)

# --- (THAY ĐỔI) ---
# 2. Khởi tạo UseCase, tiêm (inject) singleton manager vào
#    vì scheduler chạy riêng biệt, chúng ta cần dùng instance cụ thể.
notification_use_cases = NotificationUseCases(notification_repo=websocket_manager)

# 3. Chuyển hàm thành async
async def check_due_todos():
# --- (HẾT THAY ĐỔI) ---
    """
    Hàm này được gọi bởi scheduler.
    Nó tạo một session DB riêng biệt để kiểm tra các todo sắp hết hạn.
    """
    logger.info("Scheduler: Đang chạy tác vụ kiểm tra todo sắp hết hạn...")
    db: Session = sessionLocal()
    try:
        # --- (THAY ĐỔI QUAN TRỌNG) ---
        # Lấy thời gian UTC hiện tại, nhưng ở dạng NAIVE (không có múi giờ)
        # để so sánh chính xác với CSDL (vốn cũng lưu naive UTC)
        now_utc_naive = datetime.utcnow() 
        # (Lưu ý: datetime.utcnow() là cách đơn giản nhất cho việc này)
        # ---
        due_soon_limit_naive = now_utc_naive + timedelta(minutes=5)
        
        upcoming_todos = db.query(Todo).filter(
            Todo.due_date >= now_utc_naive,
            Todo.due_date <= due_soon_limit_naive,
            Todo.completed.is_(False)
        ).all()
        if not upcoming_todos:
            logger.info("Scheduler: Không tìm thấy todo nào sắp hết hạn.")
        
        for todo in upcoming_todos:
            # --- (THAY ĐỔI) ---
            # 4. Thay thế logger.warning bằng UseCase
            logger.warning(
                f"REMINDER: Todo (ID: {todo.id}) - '{todo.title}' "
                f"sẽ hết hạn lúc {todo.due_date}"
            )
            # GỌI USE CASE ĐỂ GỬI WEBSOCKET
            await notification_use_cases.send_reminder_notification(todo)
            # --- (HẾT THAY ĐỔI) ---

    except Exception as e:
        logger.error(f"Scheduler: Lỗi khi kiểm tra todos: {e}")
    finally:
        db.close()
        logger.info("Scheduler: Tác vụ hoàn tất, đóng session CSDL.")

# Khởi tạo scheduler
scheduler = AsyncIOScheduler(timezone="Asia/Ho_Chi_Minh") 

# Thêm job như hiện tại
scheduler.add_job(
    check_due_todos,        # Hàm async của chúng ta
    trigger="interval", 
    minutes=1,          
    id="check_due_todos_job",
    replace_existing=True,
)

# --- ADD: helper để start scheduler từ app startup ---
def start_scheduler() -> None:
    """
    Start the AsyncIOScheduler. Call this from FastAPI startup event.
    """
    try:
        if not getattr(scheduler, "running", False):
            scheduler.start()
            logger.info("AP Scheduler started.")
        else:
            logger.debug("AP Scheduler already running.")
    except Exception as e:
        logger.exception("Failed to start scheduler: %s", e)