"""MCP tools for persona management."""

from typing import Any, Dict

from mcp.types import Tool as MCPTool

from ._core.base import EnvironmentTokenProvider
from ._core.handlers import (
    generate_personas as _generate_personas,
    get_experiment_personas as _get_experiment_personas,
)


def generate_personas_tool() -> MCPTool:
    """Generate synthetic personas for experiments."""
    return MCPTool(
        name="generate_personas",
        description=(
            "Generate synthetic personas based on experiment configuration. "
            "Returns persona definitions that can be used in experiments."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "run_id": {
                    "type": "string",
                    "description": "The experiment run ID",
                },
                "count": {
                    "type": "integer",
                    "description": "Number of personas to generate",
                    "default": 5,
                    "minimum": 1,
                    "maximum": 20,
                },
            },
            "required": ["run_id"],
        },
    )


async def handle_generate_personas(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle generate_personas tool execution."""
    result = await _generate_personas(arguments, EnvironmentTokenProvider())
    return result.to_dict()


def get_experiment_personas_tool() -> MCPTool:
    """Get personas from a completed experiment."""
    return MCPTool(
        name="get_experiment_personas",
        description=(
            "Retrieve synthetic personas generated for a specific experiment. "
            "Returns persona descriptions and demographics."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "run_id": {
                    "type": "string",
                    "description": "The experiment run ID",
                }
            },
            "required": ["run_id"],
        },
    )


async def handle_get_experiment_personas(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle get_experiment_personas tool execution."""
    result = await _get_experiment_personas(arguments, EnvironmentTokenProvider())
    return result.to_dict()
