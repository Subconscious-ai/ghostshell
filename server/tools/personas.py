"""MCP tools for persona management."""

from typing import Any, Dict

from mcp.types import Tool as MCPTool

from ..utils.api_client import APIClient


def generate_personas_tool() -> MCPTool:
    """Generate synthetic personas for experiments."""
    return MCPTool(
        name="generate_personas",
        description=(
            "Generate synthetic personas based on trait specifications. "
            "Returns persona definitions that can be used in experiments."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "levels_per_trait": {
                    "type": "integer",
                    "description": "Number of levels per trait",
                    "default": 3,
                    "minimum": 2,
                    "maximum": 5
                },
                "trait_keys": {
                    "type": "string",
                    "description": "Comma-separated list of trait keys (e.g., 'age,gender,education')"
                }
            },
            "required": ["trait_keys"]
        }
    )


async def handle_generate_personas(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle generate_personas tool execution."""
    client = APIClient()

    try:
        params = {
            "levels_per_trait": arguments.get("levels_per_trait", 3),
            "trait_keys": arguments["trait_keys"]
        }
        response = await client.get("/api/v1/personas", params=params)
        return {
            "success": True,
            "data": response,
            "message": "Personas generated successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to generate personas"
        }


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
                    "description": "The experiment run ID"
                }
            },
            "required": ["run_id"]
        }
    )


async def handle_get_experiment_personas(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle get_experiment_personas tool execution."""
    client = APIClient()
    run_id = arguments["run_id"]

    try:
        response = await client.get(f"/api/v1/experiments/{run_id}/personas")
        return {
            "success": True,
            "data": response,
            "message": f"Personas retrieved for experiment {run_id}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to get personas for experiment {run_id}"
        }

