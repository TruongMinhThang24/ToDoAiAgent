# backend/src/todo_backend/app/scheduler.py
import logging
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session

from todo_backend.app.usecases.notification_center import NotificationCenterUseCases
from todo_backend.domain.entities.models import Todo
from todo_backend.infrastructure.database.database import sessionLocal
from todo_backend.infrastructure.repositories.notification_center_repository_impl import (
    NotificationCenterRepositoryImpl,
)

# Thiết lập logger
logger = logging.getLogger(__name__)

async def check_due_todos():
    """
    Hàm này được gọi bởi scheduler.
    Nó tạo một session DB riêng biệt để kiểm tra các todo sắp hết hạn.
    """
    logger.info("Scheduler: Đang chạy tác vụ kiểm tra todo sắp hết hạn...")
    db: Session = sessionLocal()
    try:
        # Chuẩn hoá timestamp theo UTC aware để tránh lệch timezone.
        now_utc = datetime.now(timezone.utc)
        end_time_utc = now_utc + timedelta(minutes=15)

        # Database `due_date` hiện đang lưu dạng DATETIME naive UTC.
        # Vì vậy ta convert về naive UTC khi build query SQL.
        now_for_db = now_utc.replace(tzinfo=None)
        end_time_for_db = end_time_utc.replace(tzinfo=None)

        logger.info(
            "Scheduler window: due_date from %s to %s",
            now_utc.isoformat(),
            end_time_utc.isoformat(),
        )

        query = db.query(Todo).filter(
            Todo.due_date >= now_for_db,
            Todo.due_date <= end_time_for_db,
            Todo.completed == False,
        )

        # Chỉ áp dụng nếu schema hiện có cột is_notified.
        if hasattr(Todo, "is_notified"):
            query = query.filter(Todo.is_notified == False)

        upcoming_todos = query.all()
        if not upcoming_todos:
            logger.info("Scheduler: Không tìm thấy todo nào sắp hết hạn.")

        notification_service = NotificationCenterUseCases(NotificationCenterRepositoryImpl(db))
        
        for todo in upcoming_todos:
            logger.warning(
                f"REMINDER: Todo (ID: {todo.id}) - '{todo.title}' "
                f"sẽ hết hạn lúc {todo.due_date}"
            )
            await notification_service.create_due_soon_notification(todo)

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