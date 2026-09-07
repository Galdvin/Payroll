import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("payroll.audit")
logger.setLevel(logging.INFO)


class SecurityAndAuditMiddleware(BaseHTTPMiddleware):
    """Middleware enforcing security headers and structured audit logging."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = (time.time() - start_time) * 1000
        response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"

        logger.info(
            f"METHOD={request.method} PATH={request.url.path} STATUS={response.status_code} TIME={process_time:.2f}ms"
        )
        return response
