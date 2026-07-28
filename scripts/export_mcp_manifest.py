#!/usr/bin/env python3
"""Export the canonical hosted tool registry as a public MCP manifest."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

MANIFEST_PATH = Path("mcp-tools.public.json")
SOURCE_REPOSITORY = "Subconscious-ai/ghostshell"
SOURCE_PATHS = [
    Path("api/index.py"),
    *sorted(
        path.relative_to(REPO_ROOT)
        for path in (REPO_ROOT / "server" / "tools").rglob("*.py")
    ),
]


class ManifestError(ValueError):
    """Raised when the manifest does not match its canonical source."""


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode()
    return hashlib.sha256(payload).hexdigest()


def _normalized_tools(tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized = [
        {
            "name": tool["name"],
            "description": tool["description"],
            "inputSchema": tool["inputSchema"],
        }
        for tool in tools
    ]
    return sorted(normalized, key=lambda tool: tool["name"])


def build_manifest(
    *,
    tools: list[dict[str, Any]],
    source_revision: str,
    generated_at: str,
) -> dict[str, Any]:
    """Build a deterministic, secret-free public description of MCP tools."""
    normalized_tools = _normalized_tools(tools)
    return {
        "manifest_version": 1,
        "source": {
            "repository": SOURCE_REPOSITORY,
            "revision": source_revision,
        },
        "generated_at": generated_at,
        "transport": {
            "type": "stdio",
            "status": "supported",
        },
        "authentication": {
            "type": "bearer",
            "delivery": "environment",
            "environment_variable": "AUTH0_JWT_TOKEN",
        },
        "tool_count": len(normalized_tools),
        "tools_sha256": canonical_sha256(normalized_tools),
        "tools": normalized_tools,
    }


def validate_manifest(
    manifest: dict[str, Any],
    tools: list[dict[str, Any]],
) -> None:
    """Reject drift between the checked manifest and the tool registry."""
    normalized_tools = _normalized_tools(tools)
    expected_digest = canonical_sha256(normalized_tools)
    if manifest.get("tools_sha256") != expected_digest:
        raise ManifestError("tool registry digest does not match manifest")
    if manifest.get("tool_count") != len(normalized_tools):
        raise ManifestError("tool registry count does not match manifest")
    if manifest.get("tools") != normalized_tools:
        raise ManifestError("tool registry contents do not match manifest")


def _git_output(*args: str, text: bool = True) -> str | bytes:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=text,
    )
    return result.stdout.strip() if text else result.stdout


def source_revision() -> tuple[str, str]:
    revision = str(
        _git_output(
            "log",
            "-1",
            "--no-merges",
            "--format=%H",
            "--",
            *(str(path) for path in SOURCE_PATHS),
        )
    )
    generated_at = str(_git_output("show", "-s", "--format=%cI", revision))
    return revision, generated_at


def validate_source_revision(revision: str) -> None:
    """Prove that the named commit contains every current registry source."""
    for path in SOURCE_PATHS:
        committed = bytes(
            _git_output(
                "show",
                f"{revision}:{path}",
                text=False,
            )
        )
        current = (REPO_ROOT / path).read_bytes()
        if committed != current:
            raise ManifestError(
                f"source revision {revision} does not contain current {path}"
            )


def main() -> None:
    from api.index import _list_tools_payload

    tools = _list_tools_payload()
    revision, generated_at = source_revision()
    validate_source_revision(revision)
    manifest = build_manifest(
        tools=tools,
        source_revision=revision,
        generated_at=generated_at,
    )
    validate_manifest(manifest, tools)
    output = REPO_ROOT / MANIFEST_PATH
    output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(f"Wrote {output} ({manifest['tool_count']} tools)")


if __name__ == "__main__":
    main()
