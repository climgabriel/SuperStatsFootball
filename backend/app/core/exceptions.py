from fastapi import HTTPException, status


class SuperStatsException(Exception):
    """Base exception for SuperStatsFootball."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class AuthenticationError(SuperStatsException):
    """Raised when authentication fails."""
    pass


class AuthorizationError(SuperStatsException):
    """Raised when user lacks permissions."""
    pass


class ResourceNotFoundError(SuperStatsException):
    """Raised when a resource is not found."""
    pass


class ValidationError(SuperStatsException):
    """Raised when validation fails."""
    pass


class APIFootballError(SuperStatsException):
    """Raised when API-Football request fails."""
    pass


class TierLimitError(SuperStatsException):
    """Raised when user exceeds tier limits."""
    pass


class RateLimitError(SuperStatsException):
    """Raised when rate limit is exceeded."""
    pass


# HTTP Exception helpers
def not_found_exception(detail: str):
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def unauthorized_exception(detail: str = "Not authenticated"):
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"}
    )


def forbidden_exception(detail: str = "Not enough permissions"):
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


def bad_request_exception(detail: str):
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
