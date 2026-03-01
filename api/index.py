"""Subconscious AI MCP Server - Vercel Deployment.

Remote MCP server for AI assistants to run conjoint experiments.
Supports MCP protocol via SSE for Cursor/Claude Desktop integration.
"""

import asyncio
import json
import logging
import uuid
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, Optional

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse
from starlette.routing import Route

from server.config import config
from server.tools import (
    check_causality_tool,
    create_experiment_tool,
    generate_attributes_levels_tool,
    generate_personas_tool,
    get_amce_data_tool,
    get_causal_insights_tool,
    get_experiment_personas_tool,
    get_experiment_results_tool,
    get_experiment_status_tool,
    get_population_stats_tool,
    get_run_artifacts_tool,
    get_run_details_tool,
    list_experiments_tool,
    update_run_config_tool,
    validate_population_tool,
)
from server.tools._core.base import RequestTokenProvider, ToolResult
from server.tools._core.handlers import (
    check_causality as check_causality_handler,
)
from server.tools._core.handlers import (
    create_experiment as create_experiment_handler,
)
from server.tools._core.handlers import (
    generate_attributes_levels as generate_attributes_levels_handler,
)
from server.tools._core.handlers import (
    generate_personas as generate_personas_handler,
)
from server.tools._core.handlers import (
    get_amce_data as get_amce_data_handler,
)
from server.tools._core.handlers import (
    get_causal_insights as get_causal_insights_handler,
)
from server.tools._core.handlers import (
    get_experiment_personas as get_experiment_personas_handler,
)
from server.tools._core.handlers import (
    get_experiment_results as get_experiment_results_handler,
)
from server.tools._core.handlers import (
    get_experiment_status as get_experiment_status_handler,
)
from server.tools._core.handlers import (
    get_population_stats as get_population_stats_handler,
)
from server.tools._core.handlers import (
    get_run_artifacts as get_run_artifacts_handler,
)
from server.tools._core.handlers import (
    get_run_details as get_run_details_handler,
)
from server.tools._core.handlers import (
    list_experiments as list_experiments_handler,
)
from server.tools._core.handlers import (
    update_run_config as update_run_config_handler,
)
from server.tools._core.handlers import (
    validate_population as validate_population_handler,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("subconscious-ai")


CoreHandler = Callable[[Dict[str, Any], RequestTokenProvider], Awaitable[ToolResult]]


@dataclass(frozen=True)
class ToolSpec:
    """Hosted tool metadata + shared core handler binding."""

    handler: CoreHandler
    description: str
    input_schema: Dict[str, Any]


# =============================================================================
# Authentication
# =============================================================================


def extract_token(request: Request) -> Optional[str]:
    """Extract JWT token from Authorization header or query param.

    Note: Query param tokens are deprecated. Prefer Authorization header.
    """
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:]

    query_token = request.query_params.get("token")
    if query_token:
        logger.warning(
            "Token passed via query param is deprecated. "
            "Use Authorization header instead for better security."
        )
    return query_token


# =============================================================================
# Tool Registry
# =============================================================================


def _build_tools() -> Dict[str, ToolSpec]:
    """Build tool registry from canonical MCP schemas and shared handlers."""
    tool_specs: Dict[str, ToolSpec] = {}
    definitions: list[tuple[Callable[[], Any], CoreHandler]] = [
        (check_causality_tool, check_causality_handler),
        (generate_attributes_levels_tool, generate_attributes_levels_handler),
        (validate_population_tool, validate_population_handler),
        (get_population_stats_tool, get_population_stats_handler),
        (create_experiment_tool, create_experiment_handler),
        (get_experiment_status_tool, get_experiment_status_handler),
        (get_experiment_results_tool, get_experiment_results_handler),
        (list_experiments_tool, list_experiments_handler),
        (get_run_details_tool, get_run_details_handler),
        (get_run_artifacts_tool, get_run_artifacts_handler),
        (update_run_config_tool, update_run_config_handler),
        (generate_personas_tool, generate_personas_handler),
        (get_experiment_personas_tool, get_experiment_personas_handler),
        (get_amce_data_tool, get_amce_data_handler),
        (get_causal_insights_tool, get_causal_insights_handler),
    ]

    for tool_factory, handler in definitions:
        tool = tool_factory()
        tool_specs[tool.name] = ToolSpec(
            handler=handler,
            description=tool.description,
            input_schema=tool.inputSchema,
        )

    return tool_specs


TOOLS = _build_tools()


def _list_tools_payload() -> list[Dict[str, Any]]:
    """List tool metadata for MCP and REST responses."""
    return [
        {
            "name": name,
            "description": spec.description,
            "inputSchema": spec.input_schema,
        }
        for name, spec in TOOLS.items()
    ]


async def execute_tool(tool_name: str, arguments: Dict[str, Any], token: str) -> Dict[str, Any]:
    """Execute a tool via the shared core handler layer."""
    spec = TOOLS[tool_name]
    result = await spec.handler(arguments, RequestTokenProvider(token))
    return result.to_dict()


# =============================================================================
# MCP Protocol over SSE
# =============================================================================

SESSIONS: Dict[str, Dict[str, Any]] = {}


async def handle_mcp_request(method: str, params: Dict[str, Any], msg_id: Any, token: str) -> Optional[Dict[str, Any]]:
    """Handle MCP JSON-RPC requests."""
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": config.server_name,
                    "version": config.server_version,
                },
            },
        }

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"tools": _list_tools_payload()},
        }

    if method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name not in TOOLS:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"},
            }

        result = await execute_tool(tool_name, arguments, token)
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "content": [
                    {"type": "text", "text": json.dumps(result, indent=2, default=str)}
                ]
            },
        }

    if method == "notifications/initialized":
        return None

    return {
        "jsonrpc": "2.0",
        "id": msg_id,
        "error": {"code": -32601, "message": f"Method not found: {method}"},
    }


async def sse_endpoint(request: Request):
    """SSE endpoint for MCP protocol - Cursor/Claude connect here."""
    token = extract_token(request)
    if not token:
        return JSONResponse(
            {
                "error": (
                    "Token required. Send Authorization: Bearer YOUR_TOKEN "
                    "or use ?token=YOUR_TOKEN"
                )
            },
            status_code=401,
        )

    session_id = str(uuid.uuid4())
    SESSIONS[session_id] = {"token": token, "responses": asyncio.Queue()}

    async def event_stream():
        yield f"event: endpoint\ndata: /api/sse/message?session_id={session_id}\n\n"

        try:
            while True:
                try:
                    response = await asyncio.wait_for(
                        SESSIONS[session_id]["responses"].get(),
                        timeout=30,
                    )
                    if response:
                        yield f"event: message\ndata: {json.dumps(response)}\n\n"
                except asyncio.TimeoutError:
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
            "X-Accel-Buffering": "no",
        },
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
            session["token"],
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
    return JSONResponse(
        {
            "status": "healthy",
            "server": config.server_name,
            "version": config.server_version,
            "tools": len(TOOLS),
        }
    )


async def server_info(request: Request) -> JSONResponse:
    return JSONResponse(
        {
            "name": config.server_name,
            "version": config.server_version,
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
                },
            },
        }
    )


async def list_tools_endpoint(request: Request) -> JSONResponse:
    tools_list = _list_tools_payload()
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

    result = await execute_tool(tool_name, body, token)
    return JSONResponse(result)


# =============================================================================
# Application
# =============================================================================

_cors_config: Dict[str, Any] = {
    "allow_origins": config.cors_allowed_origins,
    "allow_methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Authorization", "Content-Type"],
    "allow_credentials": config.cors_allow_credentials,
}
if config.cors_origin_regex:
    _cors_config["allow_origin_regex"] = config.cors_origin_regex

middleware = [Middleware(CORSMiddleware, **_cors_config)]

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
    middleware=middleware,
)
