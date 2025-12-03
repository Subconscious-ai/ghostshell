"""MCP tools for analytics and insights."""

from typing import Any, Dict

from mcp.types import Tool as MCPTool

from ..utils.api_client import APIClient


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
                    "description": "The experiment run ID"
                },
                "format": {
                    "type": "string",
                    "description": "Output format",
                    "enum": ["json", "csv"],
                    "default": "json"
                }
            },
            "required": ["run_id"]
        }
    )


async def handle_get_amce_data(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle get_amce_data tool execution."""
    client = APIClient()
    run_id = arguments["run_id"]

    try:
        # Use v3 API for processed AMCE data
        response = await client.get(f"/api/v3/runs/{run_id}/processed/amce")

        return {
            "success": True,
            "data": response,
            "message": f"AMCE data retrieved for run {run_id}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to get AMCE data for run {run_id}"
        }


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
                    "description": "The experiment run ID"
                },
                "include_visualizations": {
                    "type": "boolean",
                    "description": "Whether to include visualization URLs",
                    "default": False
                }
            },
            "required": ["run_id"]
        }
    )


async def handle_get_causal_insights(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle get_causal_insights tool execution."""
    client = APIClient()
    run_id = arguments["run_id"]

    try:
        # Use v3 API for causal sentences (returns a list of sentence objects)
        response = await client.post(f"/api/v3/runs/{run_id}/generate/causal-sentences", json={})

        # Also get basic run info for R² and confidence
        run_info = await client.get(f"/api/v1/runs/{run_id}")
        configs = run_info.get("run_details", {}).get("configs", {})
        exp_design = configs.get("experiment_design", {})

        # Extract sentences from the list response
        causal_statements = []
        if isinstance(response, list):
            causal_statements = [item.get("sentence", str(item)) if isinstance(item, dict) else str(item) for item in response]
        elif isinstance(response, dict):
            causal_statements = response.get("causal_sentences") or response.get("sentences") or []

        insights = {
            "causal_statements": causal_statements,
            "r_squared": exp_design.get("r_squared"),
            "confidence_level": exp_design.get("confidence_level"),
        }

        return {
            "success": True,
            "data": insights,
            "message": f"Causal insights retrieved for run {run_id}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to get causal insights for run {run_id}"
        }

