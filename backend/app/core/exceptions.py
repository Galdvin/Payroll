from typing import Any, Optional
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse


class PayrollException(Exception):
    """Base exception for domain payroll errors."""
    def __init__(self, message: str, error_code: str = "INTERNAL_ERROR", details: Optional[Any] = None):
        self.message = message
        self.error_code = error_code
        self.details = details
        super().__init__(message)


class InsufficientPermissionsException(PayrollException):
    def __init__(self, message: str = "Insufficient permissions to perform this action."):
        super().__init__(message=message, error_code="PERMISSION_DENIED")


class InvalidCredentialsException(PayrollException):
    def __init__(self, message: str = "Invalid email or password."):
        super().__init__(message=message, error_code="INVALID_CREDENTIALS")


class TokenExpiredException(PayrollException):
    def __init__(self, message: str = "Authentication token has expired."):
        super().__init__(message=message, error_code="TOKEN_EXPIRED")


class ResourceNotFoundException(PayrollException):
    def __init__(self, resource: str, resource_id: Any):
        super().__init__(
            message=f"{resource} with identifier '{resource_id}' was not found.",
            error_code="RESOURCE_NOT_FOUND"
        )


def payroll_exception_handler(request, exc: PayrollException) -> JSONResponse:
    """Centralized JSON response envelope handler for domain exceptions."""
    status_code = status.HTTP_400_BAD_REQUEST
    if exc.error_code == "PERMISSION_DENIED":
        status_code = status.HTTP_403_FORBIDDEN
    elif exc.error_code in ("INVALID_CREDENTIALS", "TOKEN_EXPIRED"):
        status_code = status.HTTP_401_UNAUTHORIZED
    elif exc.error_code == "RESOURCE_NOT_FOUND":
        status_code = status.HTTP_404_NOT_FOUND

    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.details,
        },
    )
