"""MCP tools for ideation workflow - causality check and attribute/level generation."""

from typing import Any, Dict

from mcp.types import Tool as MCPTool

from ._core.base import EnvironmentTokenProvider
from ._core.handlers import (
    check_causality as _check_causality,
)
from ._core.handlers import (
    generate_attributes_levels as _generate_attributes_levels,
)

# =============================================================================
# STEP 1: Check Causality
# =============================================================================


def check_causality_tool() -> MCPTool:
    """Check if a research question is causal."""
    return MCPTool(
        name="check_causality",
        description=(
            "Check if a research question (why_prompt) is causal. "
            "A causal question asks about factors that influence an outcome. "
            "Example: 'What factors influence consumer preference for electric vehicles?' "
            "Returns whether the question is causal and suggestions for improvement if not."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "why_prompt": {
                    "type": "string",
                    "description": "The research question to check for causality",
                },
                "llm_model": {
                    "type": "string",
                    "description": "LLM model to use for analysis",
                    "enum": ["gpt4", "sonnet", "haiku"],
                    "default": "sonnet",
                },
            },
            "required": ["why_prompt"],
        },
    )


async def handle_check_causality(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle check_causality tool execution."""
    result = await _check_causality(arguments, EnvironmentTokenProvider())
    return result.to_dict()


# =============================================================================
# STEP 2: Generate Attributes and Levels
# =============================================================================


def generate_attributes_levels_tool() -> MCPTool:
    """Generate attributes and levels for a conjoint experiment."""
    return MCPTool(
        name="generate_attributes_levels",
        description=(
            "Generate attributes and levels for a conjoint experiment based on the research question. "
            "Attributes are the factors being tested (e.g., price, brand, features). "
            "Levels are the specific values for each attribute (e.g., $10, $20, $30 for price). "
            "This is required before creating an experiment."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "why_prompt": {
                    "type": "string",
                    "description": "The research question (must be causal)",
                },
                "country": {
                    "type": "string",
                    "description": "Target country for the experiment",
                    "default": "United States",
                },
                "year": {
                    "type": "string",
                    "description": "Year context for the experiment",
                    "default": "2024",
                },
                "attribute_count": {
                    "type": "integer",
                    "description": "Number of attributes to generate (2-10)",
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
                "llm_model": {
                    "type": "string",
                    "description": "LLM model to use",
                    "enum": ["gpt4", "sonnet", "haiku"],
                    "default": "sonnet",
                },
            },
            "required": ["why_prompt"],
        },
    )


async def handle_generate_attributes_levels(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle generate_attributes_levels tool execution."""
    result = await _generate_attributes_levels(arguments, EnvironmentTokenProvider())
    return result.to_dict()
