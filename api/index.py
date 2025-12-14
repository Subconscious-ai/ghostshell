"""Subconscious AI MCP Server - Vercel Deployment

Remote MCP server for AI assistants to run conjoint experiments.
Supports MCP protocol via SSE for Cursor/Claude Desktop integration.

External users add to ~/.cursor/mcp.json:
{
  "mcpServers": {
    "subconscious-ai": {
      "url": "https://ghostshell-runi.vercel.app/api/sse?token=YOUR_TOKEN"
    }
  }
}
"""

import asyncio
import json
import logging
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
# Logging Configuration
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("subconscious-ai")

# =============================================================================
# Configuration
# =============================================================================

API_BASE_URL = os.getenv("API_BASE_URL", "https://api.dev.subconscious.ai")
SERVER_NAME = "subconscious-ai"
SERVER_VERSION = "1.0.0"

# CORS Configuration
CORS_ORIGINS_ENV = os.getenv("CORS_ALLOWED_ORIGINS", "")
if CORS_ORIGINS_ENV:
    CORS_ALLOWED_ORIGINS = [o.strip() for o in CORS_ORIGINS_ENV.split(",") if o.strip()]
elif os.getenv("CORS_ALLOW_ALL", "").lower() in ("true", "1", "yes"):
    CORS_ALLOWED_ORIGINS = ["*"]
else:
    # Default: allow common development and production origins
    CORS_ALLOWED_ORIGINS = [
        "https://app.subconscious.ai",
        "https://holodeck.subconscious.ai",
        "https://*.vercel.app",
        "http://localhost:*",
        "http://127.0.0.1:*",
    ]


# =============================================================================
# Authentication
# =============================================================================

def extract_token(request: Request) -> Optional[str]:
    """Extract JWT token from Authorization header or query param.

    Note: Query param tokens are deprecated. Prefer Authorization header.
    """
    # Prefer Authorization header
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:]

    # Fallback to query param (deprecated)
    query_token = request.query_params.get("token")
    if query_token:
        logger.warning(
            "Token passed via query param is deprecated. "
            "Use Authorization header instead for better security."
        )
    return query_token


# =============================================================================
# API Client
# =============================================================================

async def api_request(method: str, endpoint: str, token: str, json_data: dict = None) -> Dict[str, Any]:
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
# Tool Implementations (15 tools)
# =============================================================================

async def check_causality(token: str, args: dict) -> dict:
    try:
        response = await api_request("POST", "/api/v2/copilot/causality", token, {
            "why_prompt": args["why_prompt"],
            "llm_model": args.get("llm_model", "databricks-claude-sonnet-4")
        })
        return {"success": True, "data": response}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def generate_attributes_levels(token: str, args: dict) -> dict:
    model_map = {"sonnet": "databricks-claude-sonnet-4", "gpt4": "azure-openai-gpt4"}
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
    model_map = {"sonnet": "databricks-claude-sonnet-4", "gpt4": "azure-openai-gpt4"}
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
    try:
        response = await api_request("GET", f"/api/v1/runs/{args['run_id']}", token)
        return {"success": True, "data": response}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def list_experiments(token: str, args: dict) -> dict:
    try:
        response = await api_request("GET", "/api/v1/runs/all", token)
        runs = response if isinstance(response, list) else response.get("runs", [])
        runs = runs[:args.get("limit", 20)]
        return {"success": True, "data": {"runs": runs, "count": len(runs)}}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def get_experiment_results(token: str, args: dict) -> dict:
    try:
        response = await api_request("GET", f"/api/v1/runs/{args['run_id']}", token)
        return {"success": True, "data": response}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def get_amce_data(token: str, args: dict) -> dict:
    try:
        response = await api_request("GET", f"/api/v3/runs/{args['run_id']}/processed/amce", token)
        return {"success": True, "data": response}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def get_causal_insights(token: str, args: dict) -> dict:
    try:
        response = await api_request("POST", f"/api/v3/runs/{args['run_id']}/generate/causal-sentences", token, {})
        sentences = [item.get("sentence", str(item)) if isinstance(item, dict) else str(item) for item in response] if isinstance(response, list) else []
        return {"success": True, "data": {"causal_statements": sentences}}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def validate_population(token: str, args: dict) -> dict:
    try:
        response = await api_request("POST", "/api/v1/population/validate", token, {
            "country": args.get("country", "United States of America (USA)"),
            "target_population": args.get("target_population", {})
        })
        return {"success": True, "data": response}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def get_population_stats(token: str, args: dict) -> dict:
    try:
        country = args.get("country", "United States of America (USA)")
        response = await api_request("GET", f"/api/v1/population/stats?country={country}", token)
        return {"success": True, "data": response}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def get_run_details(token: str, args: dict) -> dict:
    try:
        response = await api_request("GET", f"/api/v1/runs/{args['run_id']}", token)
        return {"success": True, "data": response}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def get_run_artifacts(token: str, args: dict) -> dict:
    try:
        response = await api_request("GET", f"/api/v3/runs/{args['run_id']}/artifacts", token)
        return {"success": True, "data": response}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def update_run_config(token: str, args: dict) -> dict:
    try:
        response = await api_request("POST", f"/api/v1/runs/{args['run_id']}/config", token, args.get("config", {}))
        return {"success": True, "data": response}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def generate_personas(token: str, args: dict) -> dict:
    try:
        response = await api_request("POST", f"/api/v3/runs/{args['run_id']}/generate/personas", token, {"count": args.get("count", 5)})
        return {"success": True, "data": response}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def get_experiment_personas(token: str, args: dict) -> dict:
    try:
        response = await api_request("GET", f"/api/v3/runs/{args['run_id']}/personas", token)
        return {"success": True, "data": response}
    except Exception as e:
        return {"success": False, "error": str(e)}


# =============================================================================
# Tool Registry with MCP Schemas
# =============================================================================

TOOLS = {
    "check_causality": {
        "handler": check_causality,
        "description": "Check if a research question is causal. Run this first before creating an experiment.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "why_prompt": {"type": "string", "description": "The research question to validate"}
            },
            "required": ["why_prompt"]
        }
    },
    "generate_attributes_levels": {
        "handler": generate_attributes_levels,
        "description": "Generate attributes and levels for a conjoint experiment.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "why_prompt": {"type": "string", "description": "The causal research question"},
                "attribute_count": {"type": "integer", "default": 5},
                "level_count": {"type": "integer", "default": 4}
            },
            "required": ["why_prompt"]
        }
    },
    "validate_population": {
        "handler": validate_population,
        "description": "Validate target population demographics.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "country": {"type": "string", "default": "United States of America (USA)"},
                "target_population": {"type": "object"}
            }
        }
    },
    "get_population_stats": {
        "handler": get_population_stats,
        "description": "Get population statistics for a country.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "country": {"type": "string", "default": "United States of America (USA)"}
            }
        }
    },
    "create_experiment": {
        "handler": create_experiment,
        "description": "Create and run a conjoint experiment.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "why_prompt": {"type": "string", "description": "The research question"},
                "confidence_level": {"type": "string", "enum": ["Low", "Reasonable", "High"], "default": "Low"}
            },
            "required": ["why_prompt"]
        }
    },
    "get_experiment_status": {
        "handler": get_experiment_status,
        "description": "Check experiment status.",
        "inputSchema": {
            "type": "object",
            "properties": {"run_id": {"type": "string"}},
            "required": ["run_id"]
        }
    },
    "get_experiment_results": {
        "handler": get_experiment_results,
        "description": "Get experiment results.",
        "inputSchema": {
            "type": "object",
            "properties": {"run_id": {"type": "string"}},
            "required": ["run_id"]
        }
    },
    "list_experiments": {
        "handler": list_experiments,
        "description": "List all experiments.",
        "inputSchema": {
            "type": "object",
            "properties": {"limit": {"type": "integer", "default": 20}}
        }
    },
    "get_run_details": {
        "handler": get_run_details,
        "description": "Get detailed run information.",
        "inputSchema": {
            "type": "object",
            "properties": {"run_id": {"type": "string"}},
            "required": ["run_id"]
        }
    },
    "get_run_artifacts": {
        "handler": get_run_artifacts,
        "description": "Get run artifacts and files.",
        "inputSchema": {
            "type": "object",
            "properties": {"run_id": {"type": "string"}},
            "required": ["run_id"]
        }
    },
    "update_run_config": {
        "handler": update_run_config,
        "description": "Update run configuration.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "run_id": {"type": "string"},
                "config": {"type": "object"}
            },
            "required": ["run_id"]
        }
    },
    "generate_personas": {
        "handler": generate_personas,
        "description": "Generate AI personas for experiment.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "run_id": {"type": "string"},
                "count": {"type": "integer", "default": 5}
            },
            "required": ["run_id"]
        }
    },
    "get_experiment_personas": {
        "handler": get_experiment_personas,
        "description": "Get experiment personas.",
        "inputSchema": {
            "type": "object",
            "properties": {"run_id": {"type": "string"}},
            "required": ["run_id"]
        }
    },
    "get_amce_data": {
        "handler": get_amce_data,
        "description": "Get AMCE analytics data.",
        "inputSchema": {
            "type": "object",
            "properties": {"run_id": {"type": "string"}},
            "required": ["run_id"]
        }
    },
    "get_causal_insights": {
        "handler": get_causal_insights,
        "description": "Get AI-generated causal insights.",
        "inputSchema": {
            "type": "object",
            "properties": {"run_id": {"type": "string"}},
            "required": ["run_id"]
        }
    }
}


# =============================================================================
# MCP Protocol over SSE
# =============================================================================

# Session storage for SSE connections
SESSIONS: Dict[str, dict] = {}


async def handle_mcp_request(method: str, params: dict, msg_id: Any, token: str) -> dict:
    """Handle MCP JSON-RPC requests."""

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION}
            }
        }

    elif method == "tools/list":
        tools_list = [
            {"name": name, "description": info["description"], "inputSchema": info["inputSchema"]}
            for name, info in TOOLS.items()
        ]
        return {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": tools_list}}

    elif method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name not in TOOLS:
            return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}}

        try:
            result = await TOOLS[tool_name]["handler"](token, arguments)
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"content": [{"type": "text", "text": json.dumps(result, indent=2, default=str)}]}
            }
        except Exception as e:
            return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32000, "message": str(e)}}

    elif method == "notifications/initialized":
        return None  # No response for notifications

    else:
        return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}


async def sse_endpoint(request: Request):
    """SSE endpoint for MCP protocol - Cursor/Claude connect here."""
    token = extract_token(request)
    if not token:
        return JSONResponse({"error": "Token required. Add ?token=YOUR_TOKEN to URL"}, status_code=401)

    session_id = str(uuid.uuid4())
    SESSIONS[session_id] = {"token": token, "responses": asyncio.Queue()}

    async def event_stream():
        # Send endpoint info for message posting
        endpoint_event = f"event: endpoint\ndata: /api/sse/message?session_id={session_id}\n\n"
        yield endpoint_event

        try:
            while True:
                try:
                    # Wait for responses with timeout
                    response = await asyncio.wait_for(
                        SESSIONS[session_id]["responses"].get(),
                        timeout=30
                    )
                    if response:
                        yield f"event: message\ndata: {json.dumps(response)}\n\n"
                except asyncio.TimeoutError:
                    # Send keepalive
                    yield ": keepalive\n\n"
        except Exception:
            pass
        finally:
            SESSIONS.pop(session_id, None)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


async def sse_message_endpoint(request: Request):
    """Handle POST messages from MCP clients."""
    session_id = request.query_params.get("session_id")

    if not session_id or session_id not in SESSIONS:
        return JSONResponse({"error": "Invalid session"}, status_code=400)

    session = SESSIONS[session_id]

    try:
        message = await request.json()
        response = await handle_mcp_request(
            message.get("method"),
            message.get("params", {}),
            message.get("id"),
            session["token"]
        )

        if response:
            await session["responses"].put(response)

        return JSONResponse({"status": "ok"})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# =============================================================================
# REST API Endpoints
# =============================================================================

async def health_check(request: Request) -> JSONResponse:
    return JSONResponse({
        "status": "healthy",
        "server": SERVER_NAME,
        "version": SERVER_VERSION,
        "tools": len(TOOLS)
    })


async def server_info(request: Request) -> JSONResponse:
    return JSONResponse({
        "name": SERVER_NAME,
        "version": SERVER_VERSION,
        "description": "MCP server for Subconscious AI conjoint experiments",
        "mcp_endpoint": "/api/sse?token=YOUR_TOKEN",
        "tools": list(TOOLS.keys()),
        "setup": {
            "cursor": "Add to ~/.cursor/mcp.json",
            "config": {
                "mcpServers": {
                    "subconscious-ai": {
                        "url": "https://ghostshell-runi.vercel.app/api/sse?token=YOUR_TOKEN"
                    }
                }
            }
        }
    })


async def list_tools_endpoint(request: Request) -> JSONResponse:
    tools_list = [
        {"name": name, "description": info["description"], "inputSchema": info["inputSchema"]}
        for name, info in TOOLS.items()
    ]
    return JSONResponse({"tools": tools_list, "count": len(tools_list)})


async def call_tool_endpoint(request: Request) -> JSONResponse:
    tool_name = request.path_params.get("tool_name")
    if tool_name not in TOOLS:
        return JSONResponse({"error": f"Unknown tool: {tool_name}"}, status_code=404)

    token = extract_token(request)
    if not token:
        return JSONResponse({"error": "Authorization required"}, status_code=401)

    try:
        body = await request.json()
    except Exception:
        body = {}

    result = await TOOLS[tool_name]["handler"](token, body)
    return JSONResponse(result)


# =============================================================================
# Application
# =============================================================================

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=CORS_ALLOWED_ORIGINS,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
        allow_credentials=True,
    )
]

app = Starlette(
    routes=[
        Route("/", endpoint=server_info),
        Route("/api", endpoint=server_info),
        Route("/api/health", endpoint=health_check),
        Route("/api/tools", endpoint=list_tools_endpoint),
        Route("/api/sse", endpoint=sse_endpoint),
        Route("/api/sse/message", endpoint=sse_message_endpoint, methods=["POST"]),
        Route("/api/call/{tool_name}", endpoint=call_tool_endpoint, methods=["POST"]),
    ],
    middleware=middleware
)
