"""Base types and protocols for tool handlers."""

from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol


@dataclass
class ToolResult:
    """Standardized tool result."""

    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result: Dict[str, Any] = {"success": self.success}
        if self.data is not None:
            result["data"] = self.data
        if self.error is not None:
            result["error"] = self.error
        if self.message is not None:
            result["message"] = self.message
        return result


class TokenProvider(Protocol):
    """Protocol for token retrieval strategies."""

    def get_token(self) -> str:
        """Get the authentication token."""
        ...


class EnvironmentTokenProvider:
    """Get token from environment variable (local mode)."""

    def get_token(self) -> str:
        """Get token from environment."""
        from server.config import get_auth_token

        return get_auth_token()


class RequestTokenProvider:
    """Get token from request (remote/SSE mode)."""

    def __init__(self, token: str):
        """Initialize with token from request."""
        self._token = token

    def get_token(self) -> str:
        """Return the stored token."""
        return self._token
