"""MCP tools for ideation workflow - causality check, moderation, and attribute/level generation."""

from typing import Any, Dict

from mcp.types import Tool as MCPTool

from ..utils.api_client import APIClient

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
                    "description": "The research question to check for causality"
                },
                "llm_model": {
                    "type": "string",
                    "description": "LLM model to use for analysis",
                    "enum": ["gpt4", "sonnet", "haiku"],
                    "default": "sonnet"
                }
            },
            "required": ["why_prompt"]
        }
    )


async def handle_check_causality(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle check_causality tool execution."""
    client = APIClient()

    # Map simple model names to actual enum values
    model_map = {
        "sonnet": "databricks-claude-sonnet-4",
        "gpt4": "azure-openai-gpt4",
        "haiku": "databricks-claude-sonnet-4"  # fallback
    }
    llm_model = model_map.get(arguments.get("llm_model", "sonnet"), "databricks-claude-sonnet-4")

    try:
        response = await client.post("/api/v1/copilot/check-causality", json={
            "why_prompt": arguments["why_prompt"],
            "llm_model": llm_model
        })

        is_causal = response.get("is_causal", False)
        return {
            "success": True,
            "data": response,
            "message": f"Question is {'causal ✓' if is_causal else 'NOT causal - see suggestions'}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to check causality"
        }


# =============================================================================
# STEP 2: Check Moderation (Content Policy)
# =============================================================================

def check_moderation_tool() -> MCPTool:
    """Check if content complies with content policy."""
    return MCPTool(
        name="check_moderation",
        description=(
            "Check if a research question complies with content policy. "
            "Flags content that contains violence, hate speech, or other policy violations. "
            "Run this before creating an experiment to ensure compliance."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "why_prompt": {
                    "type": "string",
                    "description": "The research question to check for content policy compliance"
                }
            },
            "required": ["why_prompt"]
        }
    )


async def handle_check_moderation(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle check_moderation tool execution."""
    client = APIClient()

    try:
        # URL encode the why_prompt for query string
        import urllib.parse
        encoded_prompt = urllib.parse.quote(arguments['why_prompt'])
        response = await client.post(
            f"/api/v1/copilot/check-moderation?why_prompt={encoded_prompt}",
            json={}
        )

        flagged = response.get("flagged", False)
        return {
            "success": True,
            "data": response,
            "message": f"Content {'FLAGGED - violates policy' if flagged else 'OK ✓'}"
        }
    except Exception as e:
        # Note: 500 errors from moderation are usually due to OpenAI API key issues on the server
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to check moderation (may be OpenAI API issue on server)"
        }


# =============================================================================
# STEP 3: Generate Attributes and Levels
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
                    "description": "The research question (must be causal)"
                },
                "country": {
                    "type": "string",
                    "description": "Target country for the experiment",
                    "default": "United States"
                },
                "year": {
                    "type": "string",
                    "description": "Year context for the experiment",
                    "default": "2024"
                },
                "attribute_count": {
                    "type": "integer",
                    "description": "Number of attributes to generate (2-10)",
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
                "llm_model": {
                    "type": "string",
                    "description": "LLM model to use",
                    "enum": ["gpt4", "sonnet", "haiku"],
                    "default": "sonnet"
                }
            },
            "required": ["why_prompt"]
        }
    )


async def handle_generate_attributes_levels(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle generate_attributes_levels tool execution."""
    client = APIClient()

    # Map simple model names to actual enum values
    model_map = {
        "sonnet": "databricks-claude-sonnet-4",
        "gpt4": "azure-openai-gpt4",
        "haiku": "databricks-claude-sonnet-4"
    }
    llm_model = model_map.get(arguments.get("llm_model", "sonnet"), "databricks-claude-sonnet-4")

    try:
        # Note: attributes-levels endpoint is at root of v1, no prefix
        response = await client.post("/api/v1/attributes-levels-claude", json={
            "why_prompt": arguments["why_prompt"],
            "country": arguments.get("country", "United States"),
            "year": arguments.get("year", "2024"),
            "attribute_count": arguments.get("attribute_count", 5),
            "level_count": arguments.get("level_count", 4),
            "llm_model": llm_model
        })

        # Response is a list of attributes directly
        attrs = response if isinstance(response, list) else response.get("attributes_levels", [])
        return {
            "success": True,
            "data": {"attributes_levels": attrs},
            "message": f"Generated {len(attrs)} attributes with levels"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to generate attributes and levels"
        }

