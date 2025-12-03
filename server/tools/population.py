"""MCP tools for population management."""

from typing import Any, Dict

from mcp.types import Tool as MCPTool

from ..utils.api_client import APIClient


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
                    "default": "United States"
                },
                "state": {
                    "type": "string",
                    "description": "Target state (optional)",
                    "default": ""
                },
                "year": {
                    "type": "string",
                    "description": "Year for census data",
                    "default": "2023"
                },
                "sample_size": {
                    "type": "integer",
                    "description": "Desired sample size",
                    "minimum": 100,
                    "maximum": 10000
                }
            },
            "required": ["country"]
        }
    )


async def handle_validate_population(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle validate_population tool execution."""
    client = APIClient()

    try:
        response = await client.post("/api/v1/populations/validate", json=arguments)
        return {
            "success": True,
            "data": response,
            "message": "Population validation completed"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to validate population"
        }


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
                    "default": "United States"
                },
                "state": {
                    "type": "string",
                    "description": "Target state (optional)",
                    "default": ""
                },
                "year": {
                    "type": "string",
                    "description": "Year for census data",
                    "default": "2023"
                }
            },
            "required": ["country"]
        }
    )


async def handle_get_population_stats(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle get_population_stats tool execution."""
    client = APIClient()

    try:
        # This would need to be implemented based on actual API endpoint
        # For now, using validate endpoint as proxy
        response = await client.post("/api/v1/populations/validate", json=arguments)
        return {
            "success": True,
            "data": response,
            "message": "Population statistics retrieved"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to get population statistics"
        }

