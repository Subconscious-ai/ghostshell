"""Tests for MCP tools."""


import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from server.tools.experiments import (
    create_experiment_tool,
    get_experiment_status_tool,
    list_experiments_tool,
)
from server.tools.ideation import (
    check_causality_tool,
    generate_attributes_levels_tool,
)


class TestToolDefinitions:
    """Test that tools are properly defined."""

    def test_check_causality_tool_definition(self):
        tool = check_causality_tool()
        assert tool.name == "check_causality"
        assert "why_prompt" in tool.inputSchema["properties"]
        assert "why_prompt" in tool.inputSchema["required"]

    def test_generate_attributes_levels_tool_definition(self):
        tool = generate_attributes_levels_tool()
        assert tool.name == "generate_attributes_levels"
        assert "why_prompt" in tool.inputSchema["required"]
        assert "attribute_count" in tool.inputSchema["properties"]
        assert "level_count" in tool.inputSchema["properties"]

    def test_create_experiment_tool_definition(self):
        tool = create_experiment_tool()
        assert tool.name == "create_experiment"
        assert "why_prompt" in tool.inputSchema["required"]
        assert "country" in tool.inputSchema["properties"]

    def test_get_experiment_status_tool_definition(self):
        tool = get_experiment_status_tool()
        assert tool.name == "get_experiment_status"
        assert "run_id" in tool.inputSchema["required"]

    def test_list_experiments_tool_definition(self):
        tool = list_experiments_tool()
        assert tool.name == "list_experiments"
        assert "limit" in tool.inputSchema["properties"]


class TestConfig:
    """Test configuration."""

    def test_config_loads(self):
        from server.config import config
        assert config.server_name == "subconscious-ai"
        assert config.request_timeout == 300


class TestAPIClient:
    """Test API client."""

    def test_api_client_init(self):
        from server.utils.api_client import APIClient
        client = APIClient()
        assert client.base_url == "https://api.dev.subconscious.ai"

    def test_api_client_custom_url(self):
        from server.utils.api_client import APIClient
        client = APIClient(base_url="https://custom.api.com")
        assert client.base_url == "https://custom.api.com"

