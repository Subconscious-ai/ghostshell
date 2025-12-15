"""Tests for retry decorator."""

import pytest
from unittest.mock import AsyncMock


class TestRetryDecorator:
    """Tests for the retry decorator."""

    @pytest.mark.asyncio
    async def test_successful_call_no_retry(self):
        """Test that successful calls don't retry."""
        from server.tools._core.retry import with_retry

        mock_func = AsyncMock(return_value="success")
        decorated = with_retry(max_retries=3)(mock_func)

        result = await decorated()

        assert result == "success"
        assert mock_func.call_count == 1

    @pytest.mark.asyncio
    async def test_retry_on_server_error(self):
        """Test that server errors trigger retries."""
        from server.tools._core.retry import with_retry
        from server.tools._core.exceptions import ServerError

        mock_func = AsyncMock(
            side_effect=[ServerError("500"), ServerError("500"), "success"]
        )
        decorated = with_retry(max_retries=3, base_delay=0.01)(mock_func)

        result = await decorated()

        assert result == "success"
        assert mock_func.call_count == 3

    @pytest.mark.asyncio
    async def test_retry_on_network_error(self):
        """Test that network errors trigger retries."""
        from server.tools._core.retry import with_retry
        from server.tools._core.exceptions import NetworkError

        mock_func = AsyncMock(side_effect=[NetworkError("timeout"), "success"])
        decorated = with_retry(max_retries=3, base_delay=0.01)(mock_func)

        result = await decorated()

        assert result == "success"
        assert mock_func.call_count == 2

    @pytest.mark.asyncio
    async def test_retry_on_rate_limit_error(self):
        """Test that rate limit errors trigger retries."""
        from server.tools._core.retry import with_retry
        from server.tools._core.exceptions import RateLimitError

        mock_func = AsyncMock(side_effect=[RateLimitError("429"), "success"])
        decorated = with_retry(max_retries=3, base_delay=0.01)(mock_func)

        result = await decorated()

        assert result == "success"
        assert mock_func.call_count == 2

    @pytest.mark.asyncio
    async def test_max_retries_exceeded_raises(self):
        """Test that exceeding max retries raises the exception."""
        from server.tools._core.retry import with_retry
        from server.tools._core.exceptions import NetworkError

        mock_func = AsyncMock(side_effect=NetworkError("timeout"))
        decorated = with_retry(max_retries=2, base_delay=0.01)(mock_func)

        with pytest.raises(NetworkError):
            await decorated()

        assert mock_func.call_count == 3  # Initial + 2 retries

    @pytest.mark.asyncio
    async def test_no_retry_on_auth_error(self):
        """Test that authentication errors don't trigger retries."""
        from server.tools._core.retry import with_retry
        from server.tools._core.exceptions import AuthenticationError

        mock_func = AsyncMock(side_effect=AuthenticationError("invalid token"))
        decorated = with_retry(max_retries=3, base_delay=0.01)(mock_func)

        with pytest.raises(AuthenticationError):
            await decorated()

        # Should not retry on auth errors
        assert mock_func.call_count == 1

    @pytest.mark.asyncio
    async def test_no_retry_on_validation_error(self):
        """Test that validation errors don't trigger retries."""
        from server.tools._core.retry import with_retry
        from server.tools._core.exceptions import ValidationError

        mock_func = AsyncMock(side_effect=ValidationError("bad input"))
        decorated = with_retry(max_retries=3, base_delay=0.01)(mock_func)

        with pytest.raises(ValidationError):
            await decorated()

        # Should not retry on validation errors
        assert mock_func.call_count == 1
