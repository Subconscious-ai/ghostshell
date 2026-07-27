"""Protocol-level smoke test for the supported local stdio transport."""

import asyncio

from scripts.smoke_stdio_mcp import probe_stdio


def test_stdio_initialize_and_tools_list():
    result = asyncio.run(asyncio.wait_for(probe_stdio(), timeout=10))

    assert result["server_name"] == "subconscious-ai"
    assert result["tool_count"] == 15
    assert "check_causality" in result["tool_names"]
    assert "get_causal_insights" in result["tool_names"]
