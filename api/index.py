"""Vercel serverless function for Subconscious AI MCP server.

Exposes the MCP server via SSE (Server-Sent Events) transport for remote access.
"""

import json
import os
import sys
from pathlib import Path

# Add parent directory to path for server imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import TextContent, Tool

# Import server components
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
from server.tools.analytics import handle_get_amce_data, handle_get_causal_insights
from server.tools.experiments import (
    handle_create_experiment,
    handle_get_experiment_results,
    handle_get_experiment_status,
    handle_list_experiments,
)
from server.tools.ideation import (
    handle_check_causality,
    handle_generate_attributes_levels,
)
from server.tools.personas import handle_generate_personas, handle_get_experiment_personas
from server.tools.population import handle_get_population_stats, handle_validate_population
from server.tools.runs import (
    handle_get_run_artifacts,
    handle_get_run_details,
    handle_update_run_config,
)


def create_mcp_server() -> Server:
    """Create and configure the MCP server instance."""
    mcp_server = Server(config.server_name)

    @mcp_server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            check_causality_tool(),
            generate_attributes_levels_tool(),
            validate_population_tool(),
            get_population_stats_tool(),
            create_experiment_tool(),
            get_experiment_status_tool(),
            get_experiment_results_tool(),
            list_experiments_tool(),
            get_run_details_tool(),
            get_run_artifacts_tool(),
            update_run_config_tool(),
            generate_personas_tool(),
            get_experiment_personas_tool(),
            get_amce_data_tool(),
            get_causal_insights_tool(),
        ]

    @mcp_server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        handlers = {
            "check_causality": handle_check_causality,
            "generate_attributes_levels": handle_generate_attributes_levels,
            "validate_population": handle_validate_population,
            "get_population_stats": handle_get_population_stats,
            "create_experiment": handle_create_experiment,
            "get_experiment_status": handle_get_experiment_status,
            "get_experiment_results": handle_get_experiment_results,
            "list_experiments": handle_list_experiments,
            "get_run_details": handle_get_run_details,
            "get_run_artifacts": handle_get_run_artifacts,
            "update_run_config": handle_update_run_config,
            "generate_personas": handle_generate_personas,
            "get_experiment_personas": handle_get_experiment_personas,
            "get_amce_data": handle_get_amce_data,
            "get_causal_insights": handle_get_causal_insights,
        }

        handler = handlers.get(name)
        if not handler:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

        try:
            result = await handler(arguments)
            if result.get("success"):
                text = f"{result.get('message', 'Success')}\n\n{json.dumps(result.get('data', {}), indent=2, default=str)}"
                return [TextContent(type="text", text=text)]
            else:
                text = f"{result.get('message', 'Error')}: {result.get('error', 'Unknown error')}"
                return [TextContent(type="text", text=text)]
        except Exception as e:
            return [TextContent(type="text", text=f"Error executing tool {name}: {str(e)}")]

    return mcp_server


# Create SSE transport for remote connections
sse_transport = SseServerTransport("/api/messages")
mcp_server = create_mcp_server()


async def handle_sse(request: Request) -> Response:
    """Handle SSE connection for MCP communication."""
    async with sse_transport.connect_sse(
        request.scope, request.receive, request._send
    ) as streams:
        await mcp_server.run(
            streams[0],
            streams[1],
            mcp_server.create_initialization_options()
        )
    return Response()


async def handle_messages(request: Request) -> Response:
    """Handle POST messages from MCP clients."""
    return await sse_transport.handle_post_message(request.scope, request.receive, request._send)


async def health_check(request: Request) -> JSONResponse:
    """Health check endpoint."""
    return JSONResponse({
        "status": "healthy",
        "server": config.server_name,
        "version": config.server_version,
        "tools_count": 15
    })


async def server_info(request: Request) -> JSONResponse:
    """Server information endpoint."""
    return JSONResponse({
        "name": config.server_name,
        "version": config.server_version,
        "description": "MCP server for Subconscious AI - Run conjoint experiments programmatically",
        "transport": "sse",
        "endpoints": {
            "sse": "/api/sse",
            "messages": "/api/messages",
            "health": "/api/health"
        },
        "tools": [
            "check_causality",
            "generate_attributes_levels",
            "validate_population",
            "get_population_stats",
            "create_experiment",
            "get_experiment_status",
            "get_experiment_results",
            "list_experiments",
            "get_run_details",
            "get_run_artifacts",
            "update_run_config",
            "generate_personas",
            "get_experiment_personas",
            "get_amce_data",
            "get_causal_insights",
        ],
        "documentation": "https://github.com/Subconscious-ai/subconscious-ai-mcp-toolkit"
    })


# Create Starlette app
app = Starlette(
    routes=[
        Route("/api/sse", endpoint=handle_sse),
        Route("/api/messages", endpoint=handle_messages, methods=["POST"]),
        Route("/api/health", endpoint=health_check),
        Route("/api", endpoint=server_info),
        Route("/", endpoint=server_info),
    ]
)


# Vercel handler
def handler(request, context):
    """Vercel serverless function handler."""
    import asyncio
    from starlette.testclient import TestClient
    
    # For Vercel, we use the ASGI app directly
    return app

