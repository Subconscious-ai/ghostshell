"""Subconscious AI MCP Server - Vercel Deployment

A remote MCP server that enables AI assistants to run conjoint experiments.
Supports both MCP protocol (SSE) and REST API access.

Usage:
  1. MCP Clients (Claude/Cursor): Connect via SSE at /api/sse
  2. REST API: Call tools directly at /api/call/{tool_name}

Authentication:
  All requests require: Authorization: Bearer YOUR_TOKEN
  Get your token at: https://app.subconscious.ai
"""

import json
import os
import uuid
from typing import Any, Dict, List, Optional

import httpx
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse
from starlette.routing import Route

# =============================================================================
# Configuration
# =============================================================================

API_BASE_URL = os.getenv("API_BASE_URL", "https://api.dev.subconscious.ai")
SERVER_NAME = "subconscious-ai"
SERVER_VERSION = "1.0.0"


# =============================================================================
# Authentication
# =============================================================================

def extract_token(request: Request) -> Optional[str]:
    """Extract JWT token from Authorization header or query param."""
    # Try header first
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:]
    # Try query param for SSE connections
    return request.query_params.get("token")


def require_auth(request: Request) -> tuple[Optional[str], Optional[JSONResponse]]:
    """Validate authentication. Returns (token, None) or (None, error_response)."""
    token = extract_token(request)
    if not token:
        return None, JSONResponse({
            "error": "Authorization required",
            "message": "Include 'Authorization: Bearer YOUR_TOKEN' header",
            "get_token": "https://app.subconscious.ai (Settings → Access Token)"
        }, status_code=401)
    return token, None


# =============================================================================
# API Client
# =============================================================================

async def api_request(
    method: str,
    endpoint: str,
    token: str,
    json_data: Optional[dict] = None
) -> Dict[str, Any]:
    """Make authenticated API request to Subconscious AI backend."""
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


# =============================================================================
# Tool Implementations
# =============================================================================

async def check_causality(token: str, args: dict) -> dict:
    """Check if a research question is properly causal."""
    try:
        response = await api_request("POST", "/api/v2/copilot/causality", token, {
            "why_prompt": args["why_prompt"],
            "llm_model": args.get("llm_model", "databricks-claude-sonnet-4")
        })
        return {"success": True, "data": response}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def generate_attributes_levels(token: str, args: dict) -> dict:
    """Generate attributes and levels for a conjoint experiment."""
    model_map = {
        "sonnet": "databricks-claude-sonnet-4",
        "gpt4": "azure-openai-gpt4",
        "haiku": "databricks-claude-sonnet-4"
    }
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
    """Create and run a conjoint experiment."""
    model_map = {
        "sonnet": "databricks-claude-sonnet-4",
        "gpt4": "azure-openai-gpt4",
        "haiku": "databricks-claude-sonnet-4"
    }
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

    # Handle pre-cooked attributes
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
        return {
            "success": True,
            "data": response,
            "message": f"Experiment created! Run ID: {response.get('wandb_run_id', 'N/A')}"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


async def get_experiment_status(token: str, args: dict) -> dict:
    """Get the current status of an experiment."""
    try:
        response = await api_request("GET", f"/api/v1/runs/{args['run_id']}", token)
        return {"success": True, "data": response}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def list_experiments(token: str, args: dict) -> dict:
    """List all experiments for the authenticated user."""
    try:
        response = await api_request("GET", "/api/v1/runs/all", token)
        runs = response if isinstance(response, list) else response.get("runs", [])
        runs = runs[:args.get("limit", 20)]
        return {"success": True, "data": {"runs": runs, "count": len(runs)}}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def get_experiment_results(token: str, args: dict) -> dict:
    """Get detailed results from a completed experiment."""
    try:
        response = await api_request("GET", f"/api/v1/runs/{args['run_id']}", token)
        return {"success": True, "data": response}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def get_amce_data(token: str, args: dict) -> dict:
    """Get AMCE (Average Marginal Component Effects) data."""
    try:
        response = await api_request("GET", f"/api/v3/runs/{args['run_id']}/processed/amce", token)
        return {"success": True, "data": response}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def get_causal_insights(token: str, args: dict) -> dict:
    """Get AI-generated causal insights from experiment results."""
    try:
        response = await api_request(
            "POST",
            f"/api/v3/runs/{args['run_id']}/generate/causal-sentences",
            token,
            {}
        )
        if isinstance(response, list):
            sentences = [
                item.get("sentence", str(item)) if isinstance(item, dict) else str(item)
                for item in response
            ]
        else:
            sentences = []
        return {"success": True, "data": {"causal_statements": sentences}}
    except Exception as e:
        return {"success": False, "error": str(e)}


# =============================================================================
# Tool Registry
# =============================================================================

TOOLS: Dict[str, Dict[str, Any]] = {
    "check_causality": {
        "handler": check_causality,
        "description": "Check if a research question is properly causal. Run this first before creating an experiment.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "why_prompt": {
                    "type": "string",
                    "description": "The research question to validate (e.g., 'What factors influence EV purchases?')"
                },
                "llm_model": {
                    "type": "string",
                    "enum": ["sonnet", "gpt4", "haiku"],
                    "default": "sonnet"
                }
            },
            "required": ["why_prompt"]
        }
    },
    "generate_attributes_levels": {
        "handler": generate_attributes_levels,
        "description": "Generate attributes and levels for a conjoint experiment based on a research question.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "why_prompt": {
                    "type": "string",
                    "description": "The causal research question"
                },
                "country": {"type": "string", "default": "United States"},
                "attribute_count": {"type": "integer", "default": 5, "minimum": 2, "maximum": 10},
                "level_count": {"type": "integer", "default": 4, "minimum": 2, "maximum": 10}
            },
            "required": ["why_prompt"]
        }
    },
    "create_experiment": {
        "handler": create_experiment,
        "description": "Create and run a new conjoint experiment. The experiment will be queued and processed asynchronously.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "why_prompt": {
                    "type": "string",
                    "description": "The causal research question for the experiment"
                },
                "country": {"type": "string", "default": "United States"},
                "attribute_count": {"type": "integer", "default": 5},
                "level_count": {"type": "integer", "default": 4},
                "confidence_level": {
                    "type": "string",
                    "enum": ["Low", "Reasonable", "High"],
                    "default": "Low"
                },
                "is_private": {"type": "boolean", "default": False},
                "pre_cooked_attributes_and_levels_lookup": {
                    "type": "array",
                    "description": "Optional pre-defined attributes and levels"
                }
            },
            "required": ["why_prompt"]
        }
    },
    "get_experiment_status": {
        "handler": get_experiment_status,
        "description": "Check the current status of a running experiment.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "run_id": {
                    "type": "string",
                    "description": "The experiment run ID (wandb_run_id)"
                }
            },
            "required": ["run_id"]
        }
    },
    "list_experiments": {
        "handler": list_experiments,
        "description": "List all experiments for your account.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "default": 20, "maximum": 100}
            }
        }
    },
    "get_experiment_results": {
        "handler": get_experiment_results,
        "description": "Get detailed results from a completed experiment.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "run_id": {"type": "string", "description": "The experiment run ID"}
            },
            "required": ["run_id"]
        }
    },
    "get_amce_data": {
        "handler": get_amce_data,
        "description": "Get AMCE (Average Marginal Component Effects) analytics data showing the impact of each attribute level.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "run_id": {"type": "string", "description": "The experiment run ID"}
            },
            "required": ["run_id"]
        }
    },
    "get_causal_insights": {
        "handler": get_causal_insights,
        "description": "Get AI-generated causal insight statements from experiment results.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "run_id": {"type": "string", "description": "The experiment run ID"}
            },
            "required": ["run_id"]
        }
    }
}


# =============================================================================
# MCP Protocol Handlers (SSE Transport)
# =============================================================================

# Store for active SSE sessions
SSE_SESSIONS: Dict[str, dict] = {}


def create_mcp_response(id: Any, result: Any) -> dict:
    """Create a JSON-RPC 2.0 response."""
    return {"jsonrpc": "2.0", "id": id, "result": result}


def create_mcp_error(id: Any, code: int, message: str) -> dict:
    """Create a JSON-RPC 2.0 error response."""
    return {"jsonrpc": "2.0", "id": id, "error": {"code": code, "message": message}}


async def handle_mcp_message(message: dict, token: str) -> dict:
    """Process an MCP JSON-RPC message."""
    method = message.get("method")
    msg_id = message.get("id")
    params = message.get("params", {})

    if method == "initialize":
        return create_mcp_response(msg_id, {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION}
        })

    elif method == "tools/list":
        tools_list = [
            {
                "name": name,
                "description": info["description"],
                "inputSchema": info["inputSchema"]
            }
            for name, info in TOOLS.items()
        ]
        return create_mcp_response(msg_id, {"tools": tools_list})

    elif method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name not in TOOLS:
            return create_mcp_error(msg_id, -32601, f"Unknown tool: {tool_name}")

        try:
            result = await TOOLS[tool_name]["handler"](token, arguments)
            content = json.dumps(result, indent=2, default=str)
            return create_mcp_response(msg_id, {
                "content": [{"type": "text", "text": content}]
            })
        except Exception as e:
            return create_mcp_error(msg_id, -32000, str(e))

    elif method == "notifications/initialized":
        # Notification, no response needed
        return None

    else:
        return create_mcp_error(msg_id, -32601, f"Method not found: {method}")


async def sse_endpoint(request: Request):
    """SSE endpoint for MCP protocol communication."""
    token, error = require_auth(request)
    if error:
        return error

    session_id = str(uuid.uuid4())
    SSE_SESSIONS[session_id] = {"token": token, "messages": []}

    async def event_generator():
        # Send session ID so client knows where to POST messages
        yield f"event: endpoint\ndata: /api/sse/message?session_id={session_id}\n\n"

        # Keep connection alive
        import asyncio
        while session_id in SSE_SESSIONS:
            # Check for pending responses
            session = SSE_SESSIONS.get(session_id, {})
            messages = session.get("messages", [])
            while messages:
                msg = messages.pop(0)
                yield f"event: message\ndata: {json.dumps(msg)}\n\n"
            await asyncio.sleep(0.1)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


async def sse_message_endpoint(request: Request):
    """Handle POST messages for SSE MCP sessions."""
    session_id = request.query_params.get("session_id")

    if not session_id or session_id not in SSE_SESSIONS:
        return JSONResponse({"error": "Invalid session"}, status_code=400)

    session = SSE_SESSIONS[session_id]
    token = session["token"]

    try:
        message = await request.json()
        response = await handle_mcp_message(message, token)

        if response:
            session["messages"].append(response)

        return JSONResponse({"status": "ok"})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# =============================================================================
# REST API Endpoints
# =============================================================================

async def health_check(request: Request) -> JSONResponse:
    """Health check endpoint."""
    return JSONResponse({
        "status": "healthy",
        "server": SERVER_NAME,
        "version": SERVER_VERSION,
        "tools": len(TOOLS)
    })


async def server_info(request: Request) -> JSONResponse:
    """Server information and documentation."""
    base_url = str(request.base_url).rstrip("/")
    return JSONResponse({
        "name": SERVER_NAME,
        "version": SERVER_VERSION,
        "description": "MCP server for Subconscious AI - Run conjoint experiments with AI agents",
        "authentication": {
            "type": "Bearer token",
            "header": "Authorization: Bearer YOUR_TOKEN",
            "get_token": "https://app.subconscious.ai (Settings → Access Token)"
        },
        "mcp": {
            "sse_endpoint": f"{base_url}/api/sse",
            "message_endpoint": f"{base_url}/api/sse/message",
            "protocol": "MCP 2024-11-05"
        },
        "rest_api": {
            "list_tools": f"GET {base_url}/api/tools",
            "call_tool": f"POST {base_url}/api/call/{{tool_name}}"
        },
        "tools": list(TOOLS.keys()),
        "workflow": [
            "1. check_causality - Validate your research question",
            "2. generate_attributes_levels - Generate experiment design",
            "3. create_experiment - Run the experiment",
            "4. get_experiment_status - Monitor progress",
            "5. get_experiment_results - Get results",
            "6. get_causal_insights - Get AI insights"
        ]
    })


async def list_tools_endpoint(request: Request) -> JSONResponse:
    """List all available tools with their schemas."""
    tools_list = [
        {
            "name": name,
            "description": info["description"],
            "inputSchema": info["inputSchema"]
        }
        for name, info in TOOLS.items()
    ]
    return JSONResponse({"tools": tools_list})


async def call_tool_endpoint(request: Request) -> JSONResponse:
    """Call a specific tool via REST API."""
    tool_name = request.path_params.get("tool_name")

    if tool_name not in TOOLS:
        return JSONResponse({"error": f"Unknown tool: {tool_name}"}, status_code=404)

    token, error = require_auth(request)
    if error:
        return error

    try:
        body = await request.json()
    except Exception:
        body = {}

    try:
        result = await TOOLS[tool_name]["handler"](token, body)
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


# =============================================================================
# Application Setup
# =============================================================================

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"]
    )
]

app = Starlette(
    routes=[
        # Info endpoints (no auth)
        Route("/", endpoint=server_info),
        Route("/api", endpoint=server_info),
        Route("/api/health", endpoint=health_check),
        Route("/api/tools", endpoint=list_tools_endpoint),

        # MCP SSE endpoints (auth required)
        Route("/api/sse", endpoint=sse_endpoint),
        Route("/api/sse/message", endpoint=sse_message_endpoint, methods=["POST"]),

        # REST API (auth required)
        Route("/api/call/{tool_name}", endpoint=call_tool_endpoint, methods=["POST"]),
    ],
    middleware=middleware
)
