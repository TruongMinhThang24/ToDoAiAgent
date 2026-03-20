
#D:\Todos\thangtm25-Todos\Todos\backend\src\main.py
import logging
import socket
import time
from fastapi.middleware.cors import CORSMiddleware
from todo_backend.app.usecases.scheduler import start_scheduler
import psutil
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session
from todo_backend.api.security.csrf import validate_csrf_request
from todo_backend.api.routers.notifications import \
    router as notification_router
from todo_backend.api.routers.admin import router as admin_router
from todo_backend.api.routers.auth import router as auth_router
from todo_backend.api.routers.chat import router as chat_router
from todo_backend.api.routers.agent import router as agent_router
from todo_backend.api.routers.error_test import router as error_test_router
from todo_backend.api.routers.todos import router as todos_router
from todo_backend.api.routers.user import router as user_router
from todo_backend.domain.entities import models
from todo_backend.infrastructure.database.database import (engine,
                                                           sessionLocal)
#import error_handling for main.py
from todo_backend.infrastructure.error_handling.error_handler import \
    error_handler

logger = logging.getLogger(__name__)



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


@app.middleware("http")
async def csrf_middleware(request, call_next):
    """Enforce CSRF cho request ghi dữ liệu khi dùng cookie-based auth."""
    try:
        await validate_csrf_request(request)
    except HTTPException as exc:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    return await call_next(request)

#register global handling
error_handler.register_app_handlers(app)

models.Base.metadata.create_all(bind=engine)

# --- (INCLUDE ROUTER MỚI) ---
app.include_router(chat_router, prefix="/api/v1")
app.include_router(agent_router, prefix="/api/v1")
app.include_router(notification_router, prefix="/api/v1")
app.include_router(auth_router)
app.include_router(todos_router, prefix="/api/v1")
app.include_router(admin_router)
app.include_router(user_router)
app.include_router(error_test_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # Frontend dev
        "http://10.109.7.97:3000"     # Network access
    ],
    allow_credentials=True,
    allow_methods=["*"],              # GET, POST, OPTIONS, DELETE, etc.
    allow_headers=["*"],              # Authorization, Content-Type, etc.
)
@app.on_event("startup")
async def startup_event():
    logger.info("Application startup: Initializing routers and database")
    try:
        start_scheduler()
    except Exception as e:
        logger.error(f"Failed to start scheduler on startup: {e}")

@app.get("/health", status_code=200, tags=["health"])
async def health_check():
    start_time = time.time()
    results = {}

    try:
        db_start = time.time()
        db: Session = sessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        db_end = time.time()
        results["database"] = {
            "status": "connected",
            "response_time": f"{(db_end - db_start):.4f} seconds"
        }
        logger.info("Database connection successful")
    except Exception as e:
        results["database"] = {
            "status": "error",
            "error": str(e)
        }
        logger.error(f"Database connection failed: {e}")

    results["server"] = {
        "status": "running",
        "host": socket.gethostname(),
        "port": 8000
    }
    logger.info("Performing health check")

    try:
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        results["system_resources"] = {
            "memory": {
                "total": f"{memory.total / (1024 ** 3):.2f} GB",
                "available": f"{memory.available / (1024 ** 3):.2f} GB",
                "percent": f"{memory.percent} %"
            },
            "disk": {
                "total": f"{disk.total / (1024 ** 3):.2f} GB",
                "used": f"{disk.used / (1024 ** 3):.2f} GB",
                "percent": f"{disk.percent} %"
            }
        }
        logger.info("System resources check successful")
    except Exception as e:
        results["system_resources"] = {
            "status": "error",
            "error": str(e)
        }
        logger.error(f"System resources check failed: {e}")

    end_time = time.time()
    results["application"] = {
        "status": "ok" if results["database"]["status"] == "connected" else "degraded",
        "total_response_time": f"{(end_time - start_time):.4f} seconds"
    }
    logger.info(f"Health check completed in {(end_time - start_time):.4f} seconds")
    return results

