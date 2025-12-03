"""MCP tools for experiment management."""

from typing import Any, Dict

from mcp.types import Tool as MCPTool

from ..utils.api_client import APIClient


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
                    "description": "The causal research question (e.g., 'What factors influence consumer preference for electric vehicles?')"
                },
                "country": {
                    "type": "string",
                    "description": "Target country",
                    "default": "United States"
                },
                "state": {
                    "type": "string",
                    "description": "Target US state (optional)"
                },
                "attribute_count": {
                    "type": "integer",
                    "description": "Number of attributes (2-10)",
                    "default": 5,
                    "minimum": 2,
                    "maximum": 10
                },
                "level_count": {
                    "type": "integer",
                    "description": "Number of levels per attribute (2-10)",
                    "default": 4,
                    "minimum": 2,
                    "maximum": 10
                },
                "pre_cooked_attributes_and_levels_lookup": {
                    "type": "array",
                    "description": "Pre-defined attributes and levels from generate_attributes_levels",
                    "items": {"type": "array"}
                },
                "is_private": {
                    "type": "boolean",
                    "description": "Make experiment private",
                    "default": False
                },
                "expr_llm_model": {
                    "type": "string",
                    "description": "LLM model for experiment",
                    "enum": ["gpt4", "sonnet", "haiku"],
                    "default": "sonnet"
                }
            },
            "required": ["why_prompt"]
        }
    )


async def handle_create_experiment(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle create_experiment tool execution."""
    client = APIClient()

    # Map simple model names to actual enum values
    model_map = {
        "sonnet": "databricks-claude-sonnet-4",
        "gpt4": "azure-openai-gpt4",
        "haiku": "databricks-claude-sonnet-4"
    }
    llm_model = model_map.get(arguments.get("expr_llm_model", "sonnet"), "databricks-claude-sonnet-4")

    # Default target population for US-based experiments
    # Note: Don't include 'state' in target_population - it expects single enum, not list
    # The backend will use all US states by default
    default_target_population = {
        "age": [18, 75],
        "gender": ["Male", "Female"],
        "racial_group": ["White", "African American", "Asian or Pacific Islander", "Mixed race", "Other race"],
        "education_level": ["High School Diploma", "Some College", "Bachelors", "Masters", "PhD"],
        "household_income": [0, 300000],
        "number_of_children": ["0", "1", "2", "3", "4+"]
    }

    # Build experiment payload with all required fields
    # Using full country name as the UI does
    country = arguments.get("country", "United States")
    if country == "United States":
        country = "United States of America (USA)"

    payload = {
        "why_prompt": arguments["why_prompt"],
        "country": country,
        "attribute_count": arguments.get("attribute_count", 5),
        "level_count": arguments.get("level_count", 4),
        "is_private": arguments.get("is_private", False),
        "expr_llm_model": llm_model,
        "experiment_type": "conjoint",
        "confidence_level": arguments.get("confidence_level", "Low"),
        "year": "2025",
        "target_population": default_target_population,
        # Additional required fields (matching UI-created experiments)
        "latent_variables": True,
        "add_neither_option": True,
        "binary_choice": False,
        "match_population_distribution": False
    }

    if arguments.get("state"):
        payload["state"] = arguments["state"]

    if arguments.get("pre_cooked_attributes_and_levels_lookup"):
        # Transform to backend expected format: [[attr_name, [level1, level2, ...]], ...]
        # Input can be:
        # - Already correct: [[attr_name, [level1, level2, ...]], ...]
        # - From generate_attributes_levels: [{"attribute": name, "levels": [...], ...}, ...]
        # - Flat format: [[attr_name, level1, level2, ...], ...]
        raw_attrs = arguments["pre_cooked_attributes_and_levels_lookup"]
        formatted_attrs = []
        for item in raw_attrs:
            if isinstance(item, dict):
                # From generate_attributes_levels API: {"attribute": ..., "levels": [...]}
                formatted_attrs.append([item["attribute"], item["levels"]])
            elif isinstance(item, list) and len(item) >= 2:
                if isinstance(item[1], list):
                    # Already correct format: [attr_name, [levels...]]
                    formatted_attrs.append(item)
                else:
                    # Flat format: [attr_name, level1, level2, ...] -> [attr_name, [levels...]]
                    formatted_attrs.append([item[0], item[1:]])
        payload["pre_cooked_attributes_and_levels_lookup"] = formatted_attrs

    try:
        response = await client.post("/api/v1/experiments", json=payload)
        run_id = response.get("wandb_run_id", "")
        run_name = response.get("wandb_run_name", "")

        return {
            "success": True,
            "data": response,
            "message": f"Experiment created! Run ID: {run_id}, Name: {run_name}. Use get_experiment_status to track progress."
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to create experiment"
        }


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
                    "description": "The experiment run ID (wandb_run_id)"
                }
            },
            "required": ["run_id"]
        }
    )


async def handle_get_experiment_status(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle get_experiment_status tool execution."""
    client = APIClient()
    run_id = arguments["run_id"]

    try:
        response = await client.get(f"/api/v1/runs/{run_id}")
        state = response.get("state", "unknown")
        return {
            "success": True,
            "data": response,
            "message": f"Experiment status: {state}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to get status for run {run_id}"
        }


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
                    "description": "The experiment run ID"
                }
            },
            "required": ["run_id"]
        }
    )


async def handle_get_experiment_results(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle get_experiment_results tool execution."""
    client = APIClient()
    run_id = arguments["run_id"]

    try:
        response = await client.get(f"/api/v1/runs/{run_id}")
        return {
            "success": True,
            "data": response,
            "message": f"Results retrieved for run {run_id}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to get results for run {run_id}"
        }


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
                    "maximum": 100
                }
            }
        }
    )


async def handle_list_experiments(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle list_experiments tool execution."""
    client = APIClient()

    try:
        response = await client.get("/api/v1/runs/all")

        experiments = response if isinstance(response, list) else []
        limit = arguments.get("limit", 20)
        experiments = experiments[:limit]

        return {
            "success": True,
            "data": experiments,
            "count": len(experiments),
            "message": f"Found {len(experiments)} experiments"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to list experiments"
        }
