# D:\Todos\thangtm25-Todos\Todos\backend\src\todo_backend\api\routers\error_test.py

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from todo_backend.infrastructure.database.database import sessionLocal

router = APIRouter(prefix="/error-test", tags=["error-test"])

# Dependency
def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

class ErrorTestItem(BaseModel):
    name: str
    value: int = Field(gt=0, description="Value must be greater than zero")
    description: Optional[str] = None

@router.get("/http-error")
async def trigger_http_error():
    """Test HTTP exception handling"""
    raise HTTPException(status_code=404, detail="Item not found")

@router.post("/validation-error")
async def trigger_validation_error(item: ErrorTestItem):
    """
    This endpoint will trigger validation errors if:
    - name is missing
    - value is <= 0
    """
    return {"item": item}

@router.get("/database-error")
async def trigger_database_error(db: Session = Depends(get_db)):
    """Test database error handling"""
    # Intentionally cause a database error by querying a non-existent table
    db.execute(text("SELECT * FROM non_existent_table"))
    return {"message": "This should never be returned"}

@router.get("/general-error")
async def trigger_general_error():
    """Test general exception handling"""
    # Intentionally cause a general exception
    result = 1 / 0  # Division by zero
    return {"result": result}