#!/usr/bin/env python3
"""MCP server for Subconscious AI API.

Experiment Workflow:
1. check_causality - Validate research question is causal
2. generate_attributes_levels - Create experiment attributes/levels
3. validate_population (optional) - Check target population size
4. create_experiment - Run the experiment
5. get_experiment_status - Track progress
6. get_experiment_results - Get results when complete
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from server.config import config
from server.tools import (
    # Ideation (Step 1-2)
    check_causality_tool,
    # Experiments
    create_experiment_tool,
    generate_attributes_levels_tool,
    # Personas
    generate_personas_tool,
    # Analytics
    get_amce_data_tool,
    get_causal_insights_tool,
    get_experiment_personas_tool,
    get_experiment_results_tool,
    get_experiment_status_tool,
    get_population_stats_tool,
    get_run_artifacts_tool,
    # Runs
    get_run_details_tool,
    list_experiments_tool,
    update_run_config_tool,
    # Population
    validate_population_tool,
)
from server.tools.analytics import (
    handle_get_amce_data,
    handle_get_causal_insights,
)
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
from server.tools.personas import (
    handle_generate_personas,
    handle_get_experiment_personas,
)
from server.tools.population import (
    handle_get_population_stats,
    handle_validate_population,
)
from server.tools.runs import (
    handle_get_run_artifacts,
    handle_get_run_details,
    handle_update_run_config,
)

# Create MCP server instance
server = Server(config.server_name)


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools."""
    return [
        # Ideation workflow (run these first)
        check_causality_tool(),
        generate_attributes_levels_tool(),
        # Population validation
        validate_population_tool(),
        get_population_stats_tool(),
        # Experiment management
        create_experiment_tool(),
        get_experiment_status_tool(),
        get_experiment_results_tool(),
        list_experiments_tool(),
        # Run details
        get_run_details_tool(),
        get_run_artifacts_tool(),
        update_run_config_tool(),
        # Personas
        generate_personas_tool(),
        get_experiment_personas_tool(),
        # Analytics
        get_amce_data_tool(),
        get_causal_insights_tool(),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool execution."""
    handlers = {
        # Ideation
        "check_causality": handle_check_causality,
        "generate_attributes_levels": handle_generate_attributes_levels,
        # Population
        "validate_population": handle_validate_population,
        "get_population_stats": handle_get_population_stats,
        # Experiments
        "create_experiment": handle_create_experiment,
        "get_experiment_status": handle_get_experiment_status,
        "get_experiment_results": handle_get_experiment_results,
        "list_experiments": handle_list_experiments,
        # Runs
        "get_run_details": handle_get_run_details,
        "get_run_artifacts": handle_get_run_artifacts,
        "update_run_config": handle_update_run_config,
        # Personas
        "generate_personas": handle_generate_personas,
        "get_experiment_personas": handle_get_experiment_personas,
        # Analytics
        "get_amce_data": handle_get_amce_data,
        "get_causal_insights": handle_get_causal_insights,
    }

    handler = handlers.get(name)
    if not handler:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    try:
        result = await handler(arguments)

        if result.get("success"):
            text = f"{result.get('message', 'Success')}\n\n{_format_result(result.get('data', {}))}"
            return [TextContent(type="text", text=text)]
        else:
            text = f"{result.get('message', 'Error')}: {result.get('error', 'Unknown error')}"
            return [TextContent(type="text", text=text)]
    except Exception as e:
        return [TextContent(type="text", text=f"Error executing tool {name}: {str(e)}")]


def _format_result(data: dict) -> str:
    """Format result data for display."""
    import json
    return json.dumps(data, indent=2, default=str)


async def main():
    """Main entry point."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
