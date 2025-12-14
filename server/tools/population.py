"""MCP tools for population management."""

from typing import Any, Dict

from mcp.types import Tool as MCPTool

from ._core.base import EnvironmentTokenProvider
from ._core.handlers import (
    get_population_stats as _get_population_stats,
    validate_population as _validate_population,
)


def validate_population_tool() -> MCPTool:
    """Validate population configuration."""
    return MCPTool(
        name="validate_population",
        description=(
            "Validate a population configuration before running an experiment. "
            "Checks census data availability and population parameters."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "country": {
                    "type": "string",
                    "description": "Target country (e.g., 'United States')",
                    "default": "United States of America (USA)",
                },
                "target_population": {
                    "type": "object",
                    "description": "Target population demographics configuration",
                },
            },
        },
    )


async def handle_validate_population(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle validate_population tool execution."""
    result = await _validate_population(arguments, EnvironmentTokenProvider())
    return result.to_dict()


def get_population_stats_tool() -> MCPTool:
    """Get population statistics."""
    return MCPTool(
        name="get_population_stats",
        description=(
            "Get statistical information about a population configuration. "
            "Includes demographic breakdowns and census data summaries."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "country": {
                    "type": "string",
                    "description": "Target country",
                    "default": "United States of America (USA)",
                },
            },
        },
    )


async def handle_get_population_stats(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle get_population_stats tool execution."""
    result = await _get_population_stats(arguments, EnvironmentTokenProvider())
    return result.to_dict()
