"""Tests for the deterministic public MCP tool manifest."""

import json
from pathlib import Path

import pytest

from api.index import _list_tools_payload
from scripts.export_mcp_manifest import (
    MANIFEST_PATH,
    ManifestError,
    build_manifest,
    canonical_sha256,
    validate_manifest,
    validate_source_revision,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def _sample_tools() -> list[dict]:
    return [
        {
            "name": "z_tool",
            "description": "Last alphabetically",
            "inputSchema": {
                "type": "object",
                "properties": {"value": {"type": "string"}},
            },
        },
        {
            "name": "a_tool",
            "description": "First alphabetically",
            "inputSchema": {"type": "object", "properties": {}},
        },
    ]


def test_manifest_is_deterministic_versioned_and_secret_free():
    first = build_manifest(
        tools=_sample_tools(),
        source_revision="a" * 40,
        generated_at="2026-07-26T10:00:00-04:00",
    )
    second = build_manifest(
        tools=list(reversed(_sample_tools())),
        source_revision="a" * 40,
        generated_at="2026-07-26T10:00:00-04:00",
    )

    assert first == second
    assert first["manifest_version"] == 1
    assert first["source"] == {
        "repository": "Subconscious-ai/ghostshell",
        "revision": "a" * 40,
    }
    assert first["generated_at"] == "2026-07-26T10:00:00-04:00"
    assert first["transport"] == {"type": "stdio", "status": "supported"}
    assert first["authentication"] == {
        "type": "bearer",
        "delivery": "environment",
        "environment_variable": "AUTH0_JWT_TOKEN",
    }
    assert first["tool_count"] == 2
    assert [tool["name"] for tool in first["tools"]] == ["a_tool", "z_tool"]
    assert first["tools_sha256"] == canonical_sha256(first["tools"])

    serialized = json.dumps(first).lower()
    assert "your_token" not in serialized
    assert "?token=" not in serialized


def test_validation_rejects_registry_drift():
    tools = _sample_tools()
    manifest = build_manifest(
        tools=tools,
        source_revision="b" * 40,
        generated_at="2026-07-26T10:00:00-04:00",
    )

    validate_manifest(manifest, tools)

    changed = [*tools, {"name": "new_tool", "description": "new", "inputSchema": {}}]
    with pytest.raises(ManifestError, match="tool registry digest"):
        validate_manifest(manifest, changed)


def test_committed_manifest_matches_registry_and_exact_source_revision():
    manifest = json.loads((REPO_ROOT / MANIFEST_PATH).read_text())
    tools = _list_tools_payload()

    validate_manifest(manifest, tools)
    validate_source_revision(manifest["source"]["revision"])

    assert manifest["tool_count"] == 15
    assert len(manifest["source"]["revision"]) == 40
    assert all(
        character in "0123456789abcdef"
        for character in manifest["source"]["revision"]
    )


def test_public_setup_does_not_recommend_url_credentials_or_stale_docs():
    public_files = [
        REPO_ROOT / "README.md",
        REPO_ROOT / "examples/claude/config.json",
        REPO_ROOT / "examples/cursor/mcp.json",
        REPO_ROOT / "examples/local/config.json",
    ]
    public_text = "\n".join(path.read_text() for path in public_files)

    assert "?token=" not in public_text
    assert "docs.buildwithfern.com" not in public_text
    assert "experimental" in public_text.lower()
