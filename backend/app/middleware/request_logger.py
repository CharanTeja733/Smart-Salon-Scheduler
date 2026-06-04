# backend/app/middleware/request_logger.py
import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("uvicorn.access")

class RequestLoggerMiddleware(BaseHTTPMiddleware):
    """
    Logs each request with method, path, status code, and duration.
    """
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        logger.info(
            f"{request.method} {request.url.path} "
            f"status={response.status_code} "
            f"duration={process_time:.4f}s"
        )
        return response