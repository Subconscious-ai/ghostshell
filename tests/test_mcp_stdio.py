"""Protocol-level smoke test for the supported local stdio transport."""

import asyncio

import scripts.smoke_stdio_mcp as smoke


def test_stdio_initialize_and_tools_list():
    result = asyncio.run(asyncio.wait_for(smoke.probe_stdio(), timeout=10))

    assert result["server_name"] == "subconscious-ai"
    assert result["tool_count"] == 15
    assert "check_causality" in result["tool_names"]
    assert "get_causal_insights" in result["tool_names"]


def test_cli_entrypoint_enforces_the_protocol_timeout(monkeypatch, capsys):
    observed_timeouts = []
    original_wait_for = asyncio.wait_for

    async def fake_probe_stdio():
        return {"tool_count": 15}

    def recording_wait_for(awaitable, *, timeout):
        observed_timeouts.append(timeout)
        return original_wait_for(awaitable, timeout=timeout)

    monkeypatch.setattr(smoke, "probe_stdio", fake_probe_stdio)
    monkeypatch.setattr(smoke.asyncio, "wait_for", recording_wait_for)

    smoke.main()

    assert observed_timeouts == [10]
    assert '"tool_count": 15' in capsys.readouterr().out
