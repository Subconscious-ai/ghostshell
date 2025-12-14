"""MCP tools for analytics and insights."""

from typing import Any, Dict

from mcp.types import Tool as MCPTool

from ._core.base import EnvironmentTokenProvider
from ._core.handlers import (
    get_amce_data as _get_amce_data,
    get_causal_insights as _get_causal_insights,
)


def get_amce_data_tool() -> MCPTool:
    """Get Average Marginal Component Effect (AMCE) data."""
    return MCPTool(
        name="get_amce_data",
        description=(
            "Get Average Marginal Component Effect (AMCE) data from experiment results. "
            "AMCE shows the average effect of each attribute level on choice probability."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "run_id": {
                    "type": "string",
                    "description": "The experiment run ID",
                },
                "format": {
                    "type": "string",
                    "description": "Output format",
                    "enum": ["json", "csv"],
                    "default": "json",
                },
            },
            "required": ["run_id"],
        },
    )


async def handle_get_amce_data(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle get_amce_data tool execution."""
    result = await _get_amce_data(arguments, EnvironmentTokenProvider())
    return result.to_dict()


def get_causal_insights_tool() -> MCPTool:
    """Get causal insights from experiment results."""
    return MCPTool(
        name="get_causal_insights",
        description=(
            "Get causal insights and feature importance from experiment results. "
            "Includes causal statements and feature importance rankings."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "run_id": {
                    "type": "string",
                    "description": "The experiment run ID",
                },
                "include_visualizations": {
                    "type": "boolean",
                    "description": "Whether to include visualization URLs",
                    "default": False,
                },
            },
            "required": ["run_id"],
        },
    )


async def handle_get_causal_insights(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle get_causal_insights tool execution."""
    result = await _get_causal_insights(arguments, EnvironmentTokenProvider())
    return result.to_dict()
