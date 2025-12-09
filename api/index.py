"""Vercel serverless function for Subconscious AI MCP server.

Self-contained version that works in Vercel's serverless environment.
Users must provide their own JWT token in the Authorization header.
"""

import json
import os
from typing import Any, Dict, Optional

import httpx
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.dev.subconscious.ai")


def extract_token(request: Request) -> Optional[str]:
    """Extract JWT token from request Authorization header."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:]
    return None


# Simple API client
async def api_request(method: str, endpoint: str, token: str, json_data: dict = None) -> Dict[str, Any]:
    """Make authenticated API request using user's token."""
    if not token:
        raise ValueError("Authorization token required. Include 'Authorization: Bearer YOUR_TOKEN' header.")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    url = f"{API_BASE_URL}{endpoint}"
    
    async with httpx.AsyncClient(timeout=300) as client:
        if method == "GET":
            response = await client.get(url, headers=headers)
        elif method == "POST":
            response = await client.post(url, headers=headers, json=json_data or {})
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        response.raise_for_status()
        return response.json()


# Tool handlers - all require user's token
async def check_causality(token: str, args: dict) -> dict:
    """Check if research question is causal."""
    try:
        response = await api_request("POST", "/api/v1/check-causality", token, {
            "why_prompt": args["why_prompt"],
            "llm_model": args.get("llm_model", "databricks-claude-sonnet-4")
        })
        return {"success": True, "data": response}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def generate_attributes_levels(token: str, args: dict) -> dict:
    """Generate experiment attributes and levels."""
    model_map = {"sonnet": "databricks-claude-sonnet-4", "gpt4": "azure-openai-gpt4", "haiku": "databricks-claude-sonnet-4"}
    llm_model = model_map.get(args.get("llm_model", "sonnet"), "databricks-claude-sonnet-4")
    
    try:
        response = await api_request("POST", "/api/v1/attributes-levels-claude", token, {
            "why_prompt": args["why_prompt"],
            "country": args.get("country", "United States"),
            "year": args.get("year", "2024"),
            "attribute_count": args.get("attribute_count", 5),
            "level_count": args.get("level_count", 4),
            "llm_model": llm_model
        })
        attrs = response if isinstance(response, list) else response.get("attributes_levels", [])
        return {"success": True, "data": {"attributes_levels": attrs}}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def create_experiment(token: str, args: dict) -> dict:
    """Create and run an experiment."""
    model_map = {"sonnet": "databricks-claude-sonnet-4", "gpt4": "azure-openai-gpt4", "haiku": "databricks-claude-sonnet-4"}
    llm_model = model_map.get(args.get("expr_llm_model", "sonnet"), "databricks-claude-sonnet-4")
    
    country = args.get("country", "United States")
    if country == "United States":
        country = "United States of America (USA)"
    
    payload = {
        "why_prompt": args["why_prompt"],
        "country": country,
        "attribute_count": args.get("attribute_count", 5),
        "level_count": args.get("level_count", 4),
        "is_private": args.get("is_private", False),
        "expr_llm_model": llm_model,
        "experiment_type": "conjoint",
        "confidence_level": args.get("confidence_level", "Low"),
        "year": "2025",
        "target_population": {
            "age": [18, 75],
            "gender": ["Male", "Female"],
            "racial_group": ["White", "African American", "Asian or Pacific Islander", "Mixed race", "Other race"],
            "education_level": ["High School Diploma", "Some College", "Bachelors", "Masters", "PhD"],
            "household_income": [0, 300000],
            "number_of_children": ["0", "1", "2", "3", "4+"]
        },
        "latent_variables": True,
        "add_neither_option": True,
        "binary_choice": False,
        "match_population_distribution": False
    }
    
    if args.get("pre_cooked_attributes_and_levels_lookup"):
        raw_attrs = args["pre_cooked_attributes_and_levels_lookup"]
        formatted = []
        for item in raw_attrs:
            if isinstance(item, dict):
                formatted.append([item["attribute"], item["levels"]])
            elif isinstance(item, list) and len(item) >= 2:
                formatted.append(item if isinstance(item[1], list) else [item[0], item[1:]])
        payload["pre_cooked_attributes_and_levels_lookup"] = formatted
    
    try:
        response = await api_request("POST", "/api/v1/experiments", token, payload)
        return {"success": True, "data": response}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def get_experiment_status(token: str, args: dict) -> dict:
    """Get experiment status."""
    try:
        response = await api_request("GET", f"/api/v1/runs/{args['run_id']}", token)
        return {"success": True, "data": response}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def list_experiments(token: str, args: dict) -> dict:
    """List all experiments."""
    try:
        response = await api_request("GET", "/api/v1/runs/all", token)
        runs = response.get("runs", [])[:args.get("limit", 20)]
        return {"success": True, "data": {"runs": runs, "count": len(runs)}}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def get_experiment_results(token: str, args: dict) -> dict:
    """Get experiment results."""
    try:
        response = await api_request("GET", f"/api/v1/runs/{args['run_id']}", token)
        return {"success": True, "data": response}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def get_amce_data(token: str, args: dict) -> dict:
    """Get AMCE data."""
    try:
        response = await api_request("GET", f"/api/v3/runs/{args['run_id']}/processed/amce", token)
        return {"success": True, "data": response}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def get_causal_insights(token: str, args: dict) -> dict:
    """Get causal insights."""
    try:
        response = await api_request("POST", f"/api/v3/runs/{args['run_id']}/generate/causal-sentences", token, {})
        sentences = [item.get("sentence", str(item)) if isinstance(item, dict) else str(item) for item in response] if isinstance(response, list) else []
        return {"success": True, "data": {"causal_statements": sentences}}
    except Exception as e:
        return {"success": False, "error": str(e)}


# Tool definitions
TOOLS = {
    "check_causality": {
        "handler": check_causality,
        "description": "Check if a research question is causal",
        "parameters": {"why_prompt": {"type": "string", "required": True}}
    },
    "generate_attributes_levels": {
        "handler": generate_attributes_levels,
        "description": "Generate attributes and levels for a conjoint experiment",
        "parameters": {"why_prompt": {"type": "string", "required": True}}
    },
    "create_experiment": {
        "handler": create_experiment,
        "description": "Create and run a conjoint experiment",
        "parameters": {"why_prompt": {"type": "string", "required": True}}
    },
    "get_experiment_status": {
        "handler": get_experiment_status,
        "description": "Get the status of an experiment",
        "parameters": {"run_id": {"type": "string", "required": True}}
    },
    "list_experiments": {
        "handler": list_experiments,
        "description": "List all experiments",
        "parameters": {"limit": {"type": "integer", "default": 20}}
    },
    "get_experiment_results": {
        "handler": get_experiment_results,
        "description": "Get results from a completed experiment",
        "parameters": {"run_id": {"type": "string", "required": True}}
    },
    "get_amce_data": {
        "handler": get_amce_data,
        "description": "Get AMCE (Average Marginal Component Effects) data",
        "parameters": {"run_id": {"type": "string", "required": True}}
    },
    "get_causal_insights": {
        "handler": get_causal_insights,
        "description": "Get causal insights from experiment results",
        "parameters": {"run_id": {"type": "string", "required": True}}
    }
}


# API Endpoints
async def health_check(request: Request) -> JSONResponse:
    """Health check endpoint."""
    return JSONResponse({
        "status": "healthy",
        "server": "subconscious-ai-mcp",
        "version": "1.0.0",
        "tools_count": len(TOOLS),
        "auth": "user-provided (include Authorization: Bearer YOUR_TOKEN header)"
    })


async def server_info(request: Request) -> JSONResponse:
    """Server information endpoint."""
    return JSONResponse({
        "name": "subconscious-ai-mcp",
        "version": "1.0.0",
        "description": "MCP server for Subconscious AI - Run conjoint experiments programmatically",
        "authentication": {
            "type": "Bearer token",
            "header": "Authorization: Bearer YOUR_TOKEN",
            "get_token": "https://app.subconscious.ai (Settings → Access Token after subscribing)"
        },
        "tools": list(TOOLS.keys()),
        "endpoints": {
            "health": "/api/health",
            "tools": "/api/tools",
            "call": "/api/call/{tool_name} (POST, requires auth)"
        },
        "example": {
            "curl": "curl -X POST https://ghostshell-runi.vercel.app/api/call/list_experiments -H 'Authorization: Bearer YOUR_TOKEN' -H 'Content-Type: application/json' -d '{}'"
        },
        "documentation": "https://github.com/Subconscious-ai/subconscious-ai-mcp-toolkit"
    })


async def list_tools(request: Request) -> JSONResponse:
    """List available tools."""
    tools_list = [
        {"name": name, "description": info["description"], "parameters": info["parameters"]}
        for name, info in TOOLS.items()
    ]
    return JSONResponse({"tools": tools_list})


async def call_tool(request: Request) -> JSONResponse:
    """Call a specific tool. Requires Authorization: Bearer TOKEN header."""
    tool_name = request.path_params.get("tool_name")
    
    if tool_name not in TOOLS:
        return JSONResponse({"error": f"Unknown tool: {tool_name}"}, status_code=404)
    
    # Extract user's token from Authorization header
    token = extract_token(request)
    if not token:
        return JSONResponse({
            "error": "Authorization required",
            "message": "Include 'Authorization: Bearer YOUR_TOKEN' header. Get your token from https://app.subconscious.ai after subscribing."
        }, status_code=401)
    
    try:
        body = await request.json()
    except:
        body = {}
    
    try:
        result = await TOOLS[tool_name]["handler"](token, body)
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# Create Starlette app - this is what Vercel uses
app = Starlette(
    routes=[
        Route("/", endpoint=server_info),
        Route("/api", endpoint=server_info),
        Route("/api/health", endpoint=health_check),
        Route("/api/tools", endpoint=list_tools),
        Route("/api/call/{tool_name}", endpoint=call_tool, methods=["POST"]),
    ]
)
