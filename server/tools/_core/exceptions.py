"""Custom exceptions for Subconscious AI API errors."""


class SubconsciousError(Exception):
    """Base exception for all Subconscious AI errors."""

    pass


class AuthenticationError(SubconsciousError):
    """Token invalid or expired (HTTP 401)."""

    pass


class AuthorizationError(SubconsciousError):
    """Access denied to resource (HTTP 403)."""

    pass


class NotFoundError(SubconsciousError):
    """Resource not found (HTTP 404)."""

    pass


class ValidationError(SubconsciousError):
    """Invalid request parameters (HTTP 400, 422)."""

    pass


class RateLimitError(SubconsciousError):
    """Rate limit exceeded (HTTP 429)."""

    pass


class ServerError(SubconsciousError):
    """Backend server error (HTTP 5xx)."""

    pass


class NetworkError(SubconsciousError):
    """Network connectivity or timeout issue."""

    pass
