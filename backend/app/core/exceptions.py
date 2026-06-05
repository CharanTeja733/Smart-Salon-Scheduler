from fastapi import HTTPException, status


class AppException(HTTPException):
    """Base custom exception."""
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)

class ConflictException(AppException):
    """409 Conflict - for double booking, etc."""
    def __init__(self, detail: str = "Resource conflict"):
        super().__init__(status.HTTP_409_CONFLICT, detail)

class NotFoundException(AppException):
    """404 Not Found."""
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status.HTTP_404_NOT_FOUND, detail)

class ValidationException(AppException):
    """422 Unprocessable Entity."""
    def __init__(self, detail: str = "Validation error"):
        super().__init__(status.HTTP_422_UNPROCESSABLE_ENTITY, detail)

class PaymentException(AppException):
    """400 Bad Request for payment errors."""
    def __init__(self, detail: str = "Payment processing error"):
        super().__init__(status.HTTP_400_BAD_REQUEST, detail)

class ForbiddenException(AppException):
    """403 Forbidden."""
    def __init__(self, detail: str = "Access denied"):
        super().__init__(status.HTTP_403_FORBIDDEN, detail)
