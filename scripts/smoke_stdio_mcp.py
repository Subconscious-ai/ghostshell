#!/usr/bin/env python3
"""Run a real MCP initialize + tools/list exchange over local stdio."""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

REPO_ROOT = Path(__file__).resolve().parents[1]


async def probe_stdio() -> dict[str, Any]:
    env = os.environ.copy()
    env.setdefault("AUTH0_JWT_TOKEN", "stdio-contract-smoke")
    parameters = StdioServerParameters(
        command=sys.executable,
        args=[str(REPO_ROOT / "server" / "main.py")],
        cwd=REPO_ROOT,
        env=env,
    )

    async with stdio_client(parameters) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            initialized = await session.initialize()
            listed = await session.list_tools()

    return {
        "server_name": initialized.serverInfo.name,
        "server_version": initialized.serverInfo.version,
        "tool_count": len(listed.tools),
        "tool_names": sorted(tool.name for tool in listed.tools),
    }


def main() -> None:
    result = asyncio.run(asyncio.wait_for(probe_stdio(), timeout=10))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
