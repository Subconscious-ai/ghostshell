"""HTTP client for Subconscious AI API."""

from typing import Any, Dict, Optional

import httpx

from ..config import config, get_auth_token


class APIClient:
    """HTTP client for interacting with Subconscious AI API."""

    def __init__(self, base_url: Optional[str] = None):
        """Initialize API client.

        Args:
            base_url: Optional API base URL override
        """
        self.base_url = (base_url or config.api_base_url).rstrip("/")
        self.timeout = httpx.Timeout(config.request_timeout)
        self._token: Optional[str] = None

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication."""
        if not self._token:
            self._token = get_auth_token()

        return {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }

    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Make HTTP request to API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments for httpx request

        Returns:
            JSON response data

        Raises:
            httpx.HTTPError: If request fails
        """
        url = f"{self.base_url}{endpoint}"

        # Update headers with auth token
        headers = self._get_headers()
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                **kwargs
            )
            response.raise_for_status()
            return response.json()

    async def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make GET request."""
        return await self._request("GET", endpoint, **kwargs)

    async def post(self, endpoint: str, json: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make POST request."""
        return await self._request("POST", endpoint, json=json, **kwargs)

    async def put(self, endpoint: str, json: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make PUT request."""
        return await self._request("PUT", endpoint, json=json, **kwargs)

    async def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make DELETE request."""
        return await self._request("DELETE", endpoint, **kwargs)
