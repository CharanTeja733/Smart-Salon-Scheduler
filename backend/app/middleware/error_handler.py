# backend/app/middleware/error_handler.py
import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    """
    Global exception handler to catch unhandled exceptions and return
    a consistent JSON error response.
    """
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as exc:
            logger.exception(f"Unhandled exception: {exc}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal server error. Please try again later."}
            )