"""MCP tools for run management."""

from typing import Any, Dict
from mcp.types import Tool as MCPTool

from ..utils.api_client import APIClient


def get_run_details_tool() -> MCPTool:
    """Get detailed information about a specific run."""
    return MCPTool(
        name="get_run_details",
        description=(
            "Get detailed information about a specific experiment run. "
            "Includes configuration, status, metrics, and metadata."
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


async def handle_get_run_details(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle get_run_details tool execution."""
    client = APIClient()
    run_id = arguments["run_id"]
    
    try:
        response = await client.get(f"/api/v1/runs/{run_id}")
        return {
            "success": True,
            "data": response,
            "message": f"Run details retrieved for {run_id}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to get run details for {run_id}"
        }


def get_run_artifacts_tool() -> MCPTool:
    """Get run artifacts (CSV files, images, etc.)."""
    return MCPTool(
        name="get_run_artifacts",
        description=(
            "Get artifacts from a completed experiment run. "
            "Returns download URLs for CSV files, visualizations, and other artifacts."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "run_id": {
                    "type": "string",
                    "description": "The experiment run ID"
                },
                "artifact_type": {
                    "type": "string",
                    "description": "Filter by artifact type",
                    "enum": ["csv", "image", "json", "all"],
                    "default": "all"
                }
            },
            "required": ["run_id"]
        }
    )


async def handle_get_run_artifacts(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle get_run_artifacts tool execution."""
    client = APIClient()
    run_id = arguments["run_id"]
    
    try:
        # Use v3 API for artifacts
        response = await client.get(f"/api/v3/runs/{run_id}/artifacts")
        
        # Also include artifacts from run details
        run_details = await client.get(f"/api/v1/runs/{run_id}")
        artifacts_list = run_details.get("run_details", {}).get("configs", {}).get("artifacts", [])
        
        return {
            "success": True,
            "data": {
                "artifacts": response,
                "artifact_files": artifacts_list,
                "files": run_details.get("files", [])
            },
            "message": f"Artifacts retrieved for run {run_id}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to get artifacts for run {run_id}"
        }


def update_run_config_tool() -> MCPTool:
    """Update experiment run configuration."""
    return MCPTool(
        name="update_run_config",
        description=(
            "Update configuration for an experiment run. "
            "Can update metadata, tags, and other configuration values."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "run_id": {
                    "type": "string",
                    "description": "The experiment run ID"
                },
                "config_updates": {
                    "type": "object",
                    "description": "Configuration updates to apply"
                }
            },
            "required": ["run_id", "config_updates"]
        }
    )


async def handle_update_run_config(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle update_run_config tool execution."""
    client = APIClient()
    run_id = arguments["run_id"]
    config_updates = arguments["config_updates"]
    
    try:
        response = await client.put(
            f"/api/v1/runs/{run_id}/config",
            json=config_updates
        )
        return {
            "success": True,
            "data": response,
            "message": f"Configuration updated for run {run_id}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to update configuration for run {run_id}"
        }

