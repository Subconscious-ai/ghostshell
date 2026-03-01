"""Parity tests between hosted API dispatch and shared core handlers."""

import json
from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

from server.tools._core.base import RequestTokenProvider
from server.tools._core.exceptions import AuthenticationError
from server.tools._core.handlers import check_causality


@pytest.fixture
def client():
    """Create test client."""
    from api.index import app

    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


class TestHostedParity:
    """Ensure hosted API uses the same behavior as shared handlers."""

    @pytest.mark.asyncio
    async def test_rest_tool_call_matches_core_success(self, client):
        """REST call should match core handler output on success."""
        arguments = {"why_prompt": "What influences EV adoption?"}
        token = "test-token"

        with patch("server.tools._core.handlers._api_request") as mock_request:
            mock_request.return_value = {"is_causal": True, "suggestions": []}
            expected = (
                await check_causality(arguments, RequestTokenProvider(token))
            ).to_dict()

            async with client:
                response = await client.post(
                    "/api/call/check_causality",
                    headers={"Authorization": f"Bearer {token}"},
                    json=arguments,
                )

        assert response.status_code == 200
        assert response.json() == expected

    @pytest.mark.asyncio
    async def test_rest_tool_call_matches_core_error(self, client):
        """REST call should match core handler output on errors."""
        arguments = {"why_prompt": "What influences EV adoption?"}
        token = "test-token"

        with patch("server.tools._core.handlers._api_request") as mock_request:
            mock_request.side_effect = AuthenticationError("Token expired")
            expected = (
                await check_causality(arguments, RequestTokenProvider(token))
            ).to_dict()

            async with client:
                response = await client.post(
                    "/api/call/check_causality",
                    headers={"Authorization": f"Bearer {token}"},
                    json=arguments,
                )

        assert response.status_code == 200
        assert response.json() == expected

    @pytest.mark.asyncio
    async def test_mcp_tools_call_matches_core(self):
        """MCP JSON-RPC tools/call should emit the same structured result."""
        from api.index import handle_mcp_request

        arguments = {"why_prompt": "What influences EV adoption?"}
        token = "test-token"
        msg_id = "1"

        with patch("server.tools._core.handlers._api_request") as mock_request:
            mock_request.return_value = {"is_causal": True, "suggestions": []}
            expected = (
                await check_causality(arguments, RequestTokenProvider(token))
            ).to_dict()
            response = await handle_mcp_request(
                "tools/call",
                {"name": "check_causality", "arguments": arguments},
                msg_id,
                token,
            )

        payload = response["result"]["content"][0]["text"]
        assert json.loads(payload) == expected
