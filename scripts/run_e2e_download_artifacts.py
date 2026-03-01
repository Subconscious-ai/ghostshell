#!/usr/bin/env python3
"""Run a full experiment via MCP handlers and download exposed analytics artifacts locally."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
from urllib.parse import quote

import httpx
from dotenv import load_dotenv

from server.tools._core.base import EnvironmentTokenProvider
from server.tools._core.handlers import (
    create_experiment,
    generate_attributes_levels,
    get_run_artifacts,
    get_run_details,
)


def _json_dump(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


def _extract_run_id(create_data: Dict[str, Any]) -> str | None:
    return (
        create_data.get("run_id")
        or create_data.get("wandb_run_id")
        or create_data.get("id")
        or create_data.get("wandb_id")
    )


def _state_from_details(data: Dict[str, Any]) -> str:
    if not isinstance(data, dict):
        return "unknown"
    run_details = data.get("run_details", {})
    if isinstance(run_details, dict):
        state = run_details.get("run_state") or run_details.get("state") or run_details.get("status")
        if state:
            return str(state).lower()
    return str(data.get("state") or data.get("status") or "unknown").lower()


def _collect_candidate_files(data: Any) -> set[str]:
    found: set[str] = set()

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            for k, v in node.items():
                key = str(k).lower()
                if key.endswith("_file") and isinstance(v, str):
                    found.add(v)
                elif key in {"file", "filename", "name"} and isinstance(v, str):
                    if "." in v:
                        found.add(v)
                walk(v)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(data)
    return found


async def _download_known_files(
    *,
    client: httpx.AsyncClient,
    base_url: str,
    token: str,
    run_id: str,
    artifact_payload: Any,
    out_dir: Path,
) -> list[str]:
    downloaded: list[str] = []
    headers = {"Authorization": f"Bearer {token}"}
    file_names = sorted(_collect_candidate_files(artifact_payload))
    for file_name in file_names:
        encoded = quote(file_name, safe="")
        url = f"{base_url}/api/v1/runs/artifact/{encoded}"
        try:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                out = out_dir / "files" / file_name.replace("/", "_")
                out.parent.mkdir(parents=True, exist_ok=True)
                content_type = resp.headers.get("content-type", "")
                if "application/json" in content_type:
                    _json_dump(out.with_suffix(".json"), resp.json())
                else:
                    out.write_bytes(resp.content)
                downloaded.append(file_name)
        except Exception:
            continue

    # Fallback to the most common run-scoped artifact names if nothing found.
    if not downloaded:
        fallback = [
            f"{run_id}_analytics_output.json",
            f"{run_id}_experiment_definition.json",
            f"{run_id}_survey_results.csv",
        ]
        for file_name in fallback:
            encoded = quote(file_name, safe="")
            url = f"{base_url}/api/v1/runs/artifact/{encoded}"
            try:
                resp = await client.get(url, headers=headers)
                if resp.status_code == 200:
                    out = out_dir / "files" / file_name.replace("/", "_")
                    out.parent.mkdir(parents=True, exist_ok=True)
                    content_type = resp.headers.get("content-type", "")
                    if "application/json" in content_type:
                        _json_dump(out.with_suffix(".json"), resp.json())
                    else:
                        out.write_bytes(resp.content)
                    downloaded.append(file_name)
            except Exception:
                continue

    return downloaded


async def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run experiment end-to-end and download analytics artifacts locally."
    )
    parser.add_argument(
        "--why-prompt",
        default="What factors influence consumer preference for electric vehicles?",
    )
    parser.add_argument("--country", default="United States")
    parser.add_argument("--attribute-count", type=int, default=3)
    parser.add_argument("--level-count", type=int, default=3)
    parser.add_argument("--poll-seconds", type=float, default=15.0)
    parser.add_argument("--max-wait-seconds", type=int, default=1800)
    parser.add_argument("--api-base-url", default="")
    parser.add_argument("--run-id", default="", help="Reuse existing run id; skip creation.")
    args = parser.parse_args()

    load_dotenv()
    token = os.getenv("AUTH0_JWT_TOKEN", "")
    if not token:
        print("AUTH0_JWT_TOKEN is required.")
        return 1
    base_url = args.api_base_url or os.getenv("API_BASE_URL", "")
    if not base_url:
        print("API_BASE_URL is required.")
        return 1

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = Path("artifacts") / f"e2e_{ts}"
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {out_dir}")
    print(f"API_BASE_URL={base_url}")

    tp = EnvironmentTokenProvider()

    run_id = args.run_id
    if run_id:
        print(f"Using existing run_id: {run_id}")
    else:
        attrs_res = await generate_attributes_levels(
            {
                "why_prompt": args.why_prompt,
                "country": args.country,
                "attribute_count": args.attribute_count,
                "level_count": args.level_count,
                "llm_model": "sonnet",
            },
            tp,
        )
        attrs_payload = attrs_res.to_dict()
        _json_dump(out_dir / "generate_attributes_levels.json", attrs_payload)
        if not attrs_payload.get("success"):
            print(f"generate_attributes_levels failed: {attrs_payload.get('message')}")
            return 1

        attrs = attrs_payload.get("data", {}).get("attributes_levels", [])
        create_res = await create_experiment(
            {
                "why_prompt": args.why_prompt,
                "country": args.country,
                "attribute_count": args.attribute_count,
                "level_count": args.level_count,
                "pre_cooked_attributes_and_levels_lookup": attrs[: args.attribute_count],
                "confidence_level": "Low",
            },
            tp,
        )
        create_payload = create_res.to_dict()
        _json_dump(out_dir / "create_experiment.json", create_payload)
        if not create_payload.get("success"):
            print(f"create_experiment failed: {create_payload.get('message')}")
            return 1

        run_id = _extract_run_id(create_payload.get("data", {}))
        if not run_id:
            print("Could not extract run_id from create_experiment response.")
            return 1
        print(f"Created run_id: {run_id}")

    started = time.monotonic()
    terminal = {"completed", "finished", "failed", "error", "cancelled"}
    state = "unknown"
    details_payload: Dict[str, Any] = {}
    while time.monotonic() - started < args.max_wait_seconds:
        details_res = await get_run_details({"run_id": run_id}, tp)
        details_payload = details_res.to_dict()
        _json_dump(out_dir / "get_run_details_latest.json", details_payload)
        state = _state_from_details(details_payload.get("data", {}))
        elapsed = int(time.monotonic() - started)
        print(f"run_state={state} elapsed={elapsed}s")
        if state in terminal:
            break
        await asyncio.sleep(args.poll_seconds)

    _json_dump(out_dir / "final_run_details.json", details_payload)
    if state not in terminal:
        print(f"Run did not reach terminal state within {args.max_wait_seconds}s.")
        print(f"Saved partial outputs to {out_dir}")
        return 2

    print(f"Terminal state reached: {state}")

    try:
        artifacts_res = await asyncio.wait_for(get_run_artifacts({"run_id": run_id}, tp), timeout=25)
        artifacts_payload = artifacts_res.to_dict()
    except asyncio.TimeoutError:
        artifacts_payload = {
            "success": False,
            "error": "timeout",
            "message": "Timed out calling get_run_artifacts after 25s",
            "data": {},
        }
    _json_dump(out_dir / "get_run_artifacts.json", artifacts_payload)
    if not artifacts_payload.get("success"):
        print(f"get_run_artifacts failed: {artifacts_payload.get('message')}")
    else:
        _json_dump(out_dir / "artifacts_payload_data.json", artifacts_payload.get("data"))

    # Merge in run_details-derived file names as a reliable source for downloads.
    detail_files = []
    run_details = details_payload.get("data", {}).get("run_details", {})
    if isinstance(run_details, dict):
        raw_files = run_details.get("files", [])
        if isinstance(raw_files, list):
            detail_files = raw_files
    merged_payload = {"artifact_payload": artifacts_payload.get("data"), "run_files": detail_files}

    async with httpx.AsyncClient(timeout=120) as client:
        downloaded = await _download_known_files(
            client=client,
            base_url=base_url.rstrip("/"),
            token=token,
            run_id=run_id,
            artifact_payload=merged_payload,
            out_dir=out_dir,
        )
    _json_dump(out_dir / "downloaded_files_manifest.json", {"downloaded_files": downloaded})

    print(f"Downloaded files: {len(downloaded)}")
    print(f"Done. Outputs at: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
