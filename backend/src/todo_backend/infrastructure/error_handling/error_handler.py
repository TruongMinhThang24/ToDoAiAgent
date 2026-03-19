# D:\Todos\thangtm25-Todos\Todos\backend\src\todo_backend\infrastructure\error_handling\error_handler.py

import logging
import traceback
from typing import Any, Callable, Dict, Type

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

# Configure logging
logger = logging.getLogger(__name__)

class ErrorHandler:
    """
    Global error handler for FastAPI applications following Clean Architecture.
    Handles common error types and provides a consistent JSON response format.
    """
    
    def __init__(self):
        self._handlers: Dict[Type[Exception], Callable] = {}
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """Register default error handlers for common exception types."""
        # Đăng ký từ cụ thể đến tổng quát
        self.register(HTTPException, self._handle_http_exception)
        self.register(RequestValidationError, self._handle_validation_error)
        self.register(ValidationError, self._handle_validation_error)
        self.register(SQLAlchemyError, self._handle_database_error)
        self.register(Exception, self._handle_general_exception)
    
    def register(self, exception_type: Type[Exception], handler: Callable):
        """
        Register a custom handler for a specific exception type.
        
        Args:
            exception_type: The type of exception to handle
            handler: The handler function for the exception
        """
        self._handlers[exception_type] = handler
        return self
    
    async def _handle_http_exception(self, request: Request, exc: HTTPException) -> JSONResponse:
        """Handle HTTP exceptions."""
        logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
        
        return JSONResponse(
            status_code=exc.status_code,
            content=self._format_error_response(
                message="HTTP error",
                details=exc.detail,
                status_code=exc.status_code
            ),
            headers=getattr(exc, "headers", None)
        )
    
    async def _handle_general_exception(self, request: Request, exc: Exception) -> JSONResponse:
        """Handle general exceptions."""
        error_detail = str(exc)
        logger.error(f"Unhandled exception: {error_detail}")
        logger.error(traceback.format_exc())
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=self._format_error_response(
                message="An unexpected error occurred",
                details=error_detail,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        )
    
    async def _handle_validation_error(self, request: Request, exc: Exception) -> JSONResponse:
        """Handle validation errors from Pydantic or FastAPI."""
        if isinstance(exc, RequestValidationError):
            errors = exc.errors()
        else:  # ValidationError
            errors = exc.errors()
        
        logger.warning(f"Validation error: {errors}")
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=self._format_error_response(
                message="Validation error",
                details=errors,
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        )
    
    async def _handle_database_error(self, request: Request, exc: SQLAlchemyError) -> JSONResponse:
        """Handle database-related errors."""
        error_detail = str(exc)
        logger.error(f"Database error: {error_detail}")
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=self._format_error_response(
                message="Database error occurred",
                details=error_detail,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        )
    
    def _format_error_response(self, message: str, details: Any, status_code: int) -> Dict[str, Any]:
        """
        Format the error response in a consistent structure.
        
        Args:
            message: A human-readable error message
            details: Detailed error information
            status_code: HTTP status code
            
        Returns:
            A dictionary with the formatted error response
        """
        return {
            "message": message,
            "details": details,
            "status_code": status_code
        }
    
    def register_app_handlers(self, app: FastAPI):
        """
        Register all error handlers with a FastAPI application.
        
        Args:
            app: The FastAPI application instance
        """
        # Đăng ký handler cho các exception
        for exc_type, handler in self._handlers.items():
            app.add_exception_handler(exc_type, handler)
        
        # Đăng ký handler cho lỗi 404 Not Found - chỉ cho URL không tồn tại
        # Sử dụng một hàm trung gian để phân biệt giữa 404 do URL không tồn tại và 404 do HTTPException
        @app.exception_handler(404)
        async def not_found_handler(request: Request, exc: Any):
            # Kiểm tra xem đây có phải là một HTTPException không
            if isinstance(exc, HTTPException):
                # Nếu là HTTPException, sử dụng handler cho HTTPException
                return await self._handle_http_exception(request, exc)
            else:
                # Nếu không, đây là lỗi 404 do URL không tồn tại
                logger.warning(f"404 Not Found (URL not found): {request.url}")
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content=self._format_error_response(
                        message="Resource not found",
                        details=f"The requested URL {request.url} was not found on this server",
                        status_code=status.HTTP_404_NOT_FOUND
                    )
                )
        
        logger.info(f"Registered {len(self._handlers) + 1} global error handlers")
        return self

# Create a singleton instance
error_handler = ErrorHandler()