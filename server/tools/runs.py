"""MCP tools for run management."""

from typing import Any, Dict

from mcp.types import Tool as MCPTool

from ._core.base import EnvironmentTokenProvider
from ._core.handlers import (
    get_run_artifacts as _get_run_artifacts,
    get_run_details as _get_run_details,
    update_run_config as _update_run_config,
)


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
                    "description": "The experiment run ID",
                }
            },
            "required": ["run_id"],
        },
    )


async def handle_get_run_details(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle get_run_details tool execution."""
    result = await _get_run_details(arguments, EnvironmentTokenProvider())
    return result.to_dict()


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
                    "description": "The experiment run ID",
                },
                "artifact_type": {
                    "type": "string",
                    "description": "Filter by artifact type",
                    "enum": ["csv", "image", "json", "all"],
                    "default": "all",
                },
            },
            "required": ["run_id"],
        },
    )


async def handle_get_run_artifacts(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle get_run_artifacts tool execution."""
    result = await _get_run_artifacts(arguments, EnvironmentTokenProvider())
    return result.to_dict()


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
                    "description": "The experiment run ID",
                },
                "config": {
                    "type": "object",
                    "description": "Configuration updates to apply",
                },
            },
            "required": ["run_id"],
        },
    )


async def handle_update_run_config(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle update_run_config tool execution."""
    result = await _update_run_config(arguments, EnvironmentTokenProvider())
    return result.to_dict()
