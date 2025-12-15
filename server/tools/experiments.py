"""MCP tools for experiment management."""

from typing import Any, Dict

from mcp.types import Tool as MCPTool

from ._core.base import EnvironmentTokenProvider
from ._core.handlers import (
    create_experiment as _create_experiment,
)
from ._core.handlers import (
    get_experiment_results as _get_experiment_results,
)
from ._core.handlers import (
    get_experiment_status as _get_experiment_status,
)
from ._core.handlers import (
    list_experiments as _list_experiments,
)


def create_experiment_tool() -> MCPTool:
    """Create and run a new conjoint experiment."""
    return MCPTool(
        name="create_experiment",
        description=(
            "Create and run a new conjoint experiment. "
            "The experiment will be queued for execution and run asynchronously. "
            "Returns a run ID to track progress. "
            "IMPORTANT: Run check_causality and generate_attributes_levels first!"
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "why_prompt": {
                    "type": "string",
                    "description": "The causal research question (e.g., 'What factors influence consumer preference for electric vehicles?')",
                },
                "country": {
                    "type": "string",
                    "description": "Target country",
                    "default": "United States",
                },
                "state": {
                    "type": "string",
                    "description": "Target US state (optional)",
                },
                "attribute_count": {
                    "type": "integer",
                    "description": "Number of attributes (2-10)",
                    "default": 5,
                    "minimum": 2,
                    "maximum": 10,
                },
                "level_count": {
                    "type": "integer",
                    "description": "Number of levels per attribute (2-10)",
                    "default": 4,
                    "minimum": 2,
                    "maximum": 10,
                },
                "pre_cooked_attributes_and_levels_lookup": {
                    "type": "array",
                    "description": "Pre-defined attributes and levels from generate_attributes_levels",
                    "items": {"type": "array"},
                },
                "is_private": {
                    "type": "boolean",
                    "description": "Make experiment private",
                    "default": False,
                },
                "expr_llm_model": {
                    "type": "string",
                    "description": "LLM model for experiment",
                    "enum": ["gpt4", "sonnet", "haiku"],
                    "default": "sonnet",
                },
            },
            "required": ["why_prompt"],
        },
    )


async def handle_create_experiment(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle create_experiment tool execution."""
    result = await _create_experiment(arguments, EnvironmentTokenProvider())
    return result.to_dict()


def get_experiment_status_tool() -> MCPTool:
    """Get experiment execution status."""
    return MCPTool(
        name="get_experiment_status",
        description=(
            "Get the current status of an experiment run. "
            "Returns status (running, completed, failed) and progress information."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "run_id": {
                    "type": "string",
                    "description": "The experiment run ID (wandb_run_id)",
                }
            },
            "required": ["run_id"],
        },
    )


async def handle_get_experiment_status(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle get_experiment_status tool execution."""
    result = await _get_experiment_status(arguments, EnvironmentTokenProvider())
    return result.to_dict()


def get_experiment_results_tool() -> MCPTool:
    """Get experiment results and analytics."""
    return MCPTool(
        name="get_experiment_results",
        description=(
            "Get comprehensive results from a completed experiment. "
            "Includes AMCE (Average Marginal Component Effects), insights, and visualizations."
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


async def handle_get_experiment_results(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle get_experiment_results tool execution."""
    result = await _get_experiment_results(arguments, EnvironmentTokenProvider())
    return result.to_dict()


def list_experiments_tool() -> MCPTool:
    """List all user experiments."""
    return MCPTool(
        name="list_experiments",
        description=(
            "List all experiments for the authenticated user. "
            "Returns experiment names, IDs, status, and creation dates."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum number to return",
                    "default": 20,
                    "minimum": 1,
                    "maximum": 100,
                }
            },
        },
    )


async def handle_list_experiments(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle list_experiments tool execution."""
    result = await _list_experiments(arguments, EnvironmentTokenProvider())
    return result.to_dict()
