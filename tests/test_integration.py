"""Integration tests for API endpoints."""

import pytest
from starlette.testclient import TestClient


class TestAPIEndpoints:
    """Tests for the REST API endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from api.index import app

        return TestClient(app)

    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["server"] == "subconscious-ai"
        assert data["tools"] == 15

    def test_server_info_endpoint(self, client):
        """Test server info endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "subconscious-ai"
        assert "tools" in data
        assert len(data["tools"]) == 15

    def test_tools_list_endpoint(self, client):
        """Test tools listing endpoint."""
        response = client.get("/api/tools")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 15
        tool_names = [t["name"] for t in data["tools"]]
        assert "check_causality" in tool_names
        assert "create_experiment" in tool_names
        assert "get_causal_insights" in tool_names

    def test_call_tool_without_auth_returns_401(self, client):
        """Test that calling a tool without auth returns 401."""
        response = client.post(
            "/api/call/check_causality", json={"why_prompt": "test"}
        )
        assert response.status_code == 401

    def test_call_unknown_tool_returns_404(self, client):
        """Test that calling unknown tool returns 404."""
        response = client.post(
            "/api/call/unknown_tool",
            headers={"Authorization": "Bearer test_token"},
            json={},
        )
        assert response.status_code == 404

    def test_sse_endpoint_without_token_returns_401(self, client):
        """Test that SSE endpoint requires token."""
        response = client.get("/api/sse")
        assert response.status_code == 401
        data = response.json()
        assert "token" in data["error"].lower()


class TestToolSchemas:
    """Tests for tool input schemas."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from api.index import app

        return TestClient(app)

    def test_check_causality_schema(self, client):
        """Test check_causality tool schema."""
        response = client.get("/api/tools")
        tools = {t["name"]: t for t in response.json()["tools"]}

        schema = tools["check_causality"]["inputSchema"]
        assert schema["type"] == "object"
        assert "why_prompt" in schema["properties"]
        assert "why_prompt" in schema["required"]

    def test_create_experiment_schema(self, client):
        """Test create_experiment tool schema."""
        response = client.get("/api/tools")
        tools = {t["name"]: t for t in response.json()["tools"]}

        schema = tools["create_experiment"]["inputSchema"]
        assert schema["type"] == "object"
        assert "why_prompt" in schema["properties"]
        assert "why_prompt" in schema["required"]
        assert "confidence_level" in schema["properties"]

    def test_all_tools_have_valid_schemas(self, client):
        """Test that all tools have valid schemas."""
        response = client.get("/api/tools")
        tools = response.json()["tools"]

        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool
            assert tool["inputSchema"]["type"] == "object"
            assert "properties" in tool["inputSchema"]
