"""Tests for custom exceptions."""

import pytest


class TestExceptionHierarchy:
    """Tests for exception class hierarchy."""

    def test_all_exceptions_inherit_from_base(self):
        """Test that all exceptions inherit from SubconsciousError."""
        from server.tools._core.exceptions import (
            SubconsciousError,
            AuthenticationError,
            AuthorizationError,
            NotFoundError,
            ValidationError,
            RateLimitError,
            ServerError,
            NetworkError,
        )

        assert issubclass(AuthenticationError, SubconsciousError)
        assert issubclass(AuthorizationError, SubconsciousError)
        assert issubclass(NotFoundError, SubconsciousError)
        assert issubclass(ValidationError, SubconsciousError)
        assert issubclass(RateLimitError, SubconsciousError)
        assert issubclass(ServerError, SubconsciousError)
        assert issubclass(NetworkError, SubconsciousError)

    def test_exceptions_can_be_raised_with_message(self):
        """Test that exceptions can be raised with custom messages."""
        from server.tools._core.exceptions import (
            AuthenticationError,
            ValidationError,
        )

        with pytest.raises(AuthenticationError) as exc_info:
            raise AuthenticationError("Token expired")
        assert "Token expired" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            raise ValidationError("Invalid parameter")
        assert "Invalid parameter" in str(exc_info.value)

    def test_base_exception_is_catchable(self):
        """Test that SubconsciousError can catch all child exceptions."""
        from server.tools._core.exceptions import (
            SubconsciousError,
            AuthenticationError,
            NetworkError,
        )

        exceptions_to_test = [
            AuthenticationError("test"),
            NetworkError("test"),
        ]

        for exc in exceptions_to_test:
            try:
                raise exc
            except SubconsciousError:
                pass  # Should catch all
            except Exception:
                pytest.fail(f"{type(exc).__name__} was not caught by SubconsciousError")
