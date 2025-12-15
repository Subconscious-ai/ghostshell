"""Retry decorator with exponential backoff."""

import asyncio
import logging
from functools import wraps
from typing import Any, Awaitable, Callable, ParamSpec, Tuple, Type, TypeVar

from .exceptions import NetworkError, RateLimitError, ServerError

logger = logging.getLogger("subconscious-ai")

T = TypeVar("T")
P = ParamSpec("P")

# Exceptions that should trigger a retry
RETRYABLE_ERRORS: Tuple[Type[Exception], ...] = (
    RateLimitError,
    ServerError,
    NetworkError,
)


def with_retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    exponential: bool = True,
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    """
    Retry decorator with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay between retries in seconds
        exponential: Whether to use exponential backoff (2^attempt)

    Returns:
        Decorated async function with retry logic
    """

    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception: Exception | None = None

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except RETRYABLE_ERRORS as e:
                    last_exception = e

                    if attempt < max_retries:
                        delay = base_delay * (2**attempt if exponential else 1)
                        logger.warning(
                            f"Retry {attempt + 1}/{max_retries} after {delay:.1f}s: {e}"
                        )
                        await asyncio.sleep(delay)
                    else:
                        logger.error(
                            f"Max retries ({max_retries}) exceeded: {e}"
                        )

            # If we get here, all retries failed
            if last_exception is not None:
                raise last_exception
            raise RuntimeError("Unexpected retry state")

        return wrapper

    return decorator
