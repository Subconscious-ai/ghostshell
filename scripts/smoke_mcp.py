#!/usr/bin/env python3
"""Smoke test MCP core handlers against configured backend."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

from dotenv import load_dotenv

from server.tools._core.base import EnvironmentTokenProvider
from server.tools._core.handlers import (
    create_experiment,
    generate_attributes_levels,
    generate_personas,
    get_amce_data,
    get_causal_insights,
    get_experiment_personas,
    get_population_stats,
    get_run_artifacts,
    get_run_details,
    list_experiments,
    update_run_config,
    validate_population,
)

Handler = Callable[[Dict[str, Any], EnvironmentTokenProvider], Any]


@dataclass
class SmokeCase:
    name: str
    handler: Handler
    args: Dict[str, Any]
    required: bool = True


def _fmt(data: Any, max_len: int = 220) -> str:
    text = json.dumps(data, default=str)
    if len(text) > max_len:
        return text[: max_len - 3] + "..."
    return text


async def _run_case(
    case: SmokeCase, token_provider: EnvironmentTokenProvider, timeout_seconds: float
) -> Dict[str, Any]:
    try:
        result = await asyncio.wait_for(
            case.handler(case.args, token_provider), timeout=timeout_seconds
        )
        payload = result.to_dict()
    except asyncio.TimeoutError:
        payload = {
            "success": False,
            "error": "timeout",
            "message": f"Timed out after {timeout_seconds:.0f}s",
        }
    payload["name"] = case.name
    payload["required"] = case.required
    return payload


def _extract_first_run_id(list_result: Dict[str, Any]) -> Optional[str]:
    if not list_result.get("success"):
        return None
    data = list_result.get("data", {})
    runs = data.get("runs", []) if isinstance(data, dict) else []
    if not runs:
        return None
    first = runs[0]
    if not isinstance(first, dict):
        return None
    return (
        first.get("run_id")
        or first.get("wandb_run_id")
        or first.get("id")
        or first.get("name")
    )


async def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test MCP handlers against backend API.")
    parser.add_argument("--run-id", help="Run ID to use for run-specific checks.")
    parser.add_argument(
        "--deep",
        action="store_true",
        help="Run additional run/analytics/persona checks when a run_id is available.",
    )
    parser.add_argument(
        "--exercise-create",
        action="store_true",
        help="Attempt create_experiment (writes data, optional).",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=20.0,
        help="Per-call timeout in seconds for smoke checks.",
    )
    args = parser.parse_args()

    load_dotenv()
    api_base_url = os.getenv("API_BASE_URL", "")
    token = os.getenv("AUTH0_JWT_TOKEN", "")
    print(f"API_BASE_URL={api_base_url}")
    print(f"AUTH0_JWT_TOKEN_set={bool(token)} token_len={len(token)}")

    token_provider = EnvironmentTokenProvider()
    cases: list[SmokeCase] = [
        SmokeCase("list_experiments", list_experiments, {"limit": 3}, required=True),
        SmokeCase(
            "validate_population",
            validate_population,
            {
                "country": "United States",
                "target_population": {"age": [25, 45], "gender": ["Female", "Male"]},
                "number_of_records": 250,
            },
            required=True,
        ),
        SmokeCase(
            "get_population_stats",
            get_population_stats,
            {"country": "United States"},
            required=True,
        ),
    ]

    print("\n== Core checks ==")
    results: list[Dict[str, Any]] = []
    for case in cases:
        payload = await _run_case(case, token_provider, args.timeout_seconds)
        results.append(payload)
        status = "PASS" if payload.get("success") else "FAIL"
        print(f"[{status}] {payload['name']}: {payload.get('message')}")
        if payload.get("data") is not None:
            print(f"  data: {_fmt(payload.get('data'))}")
        if payload.get("error"):
            print(f"  error: {payload.get('error')}")

    list_result = next((r for r in results if r["name"] == "list_experiments"), {})
    run_id = args.run_id or _extract_first_run_id(list_result)
    print(f"\nrun_id_selected={run_id}")

    deep_cases: list[SmokeCase] = []
    if args.deep and run_id:
        deep_cases = [
            SmokeCase("get_run_details", get_run_details, {"run_id": run_id}, required=True),
            SmokeCase("get_run_artifacts", get_run_artifacts, {"run_id": run_id}, required=False),
            SmokeCase("get_experiment_personas", get_experiment_personas, {"run_id": run_id}, required=False),
            SmokeCase("generate_personas", generate_personas, {"run_id": run_id, "count": 5}, required=False),
            SmokeCase("get_amce_data", get_amce_data, {"run_id": run_id}, required=False),
            SmokeCase("get_causal_insights", get_causal_insights, {"run_id": run_id}, required=False),
            SmokeCase(
                "update_run_config",
                update_run_config,
                {"run_id": run_id, "config": {"set_privacy": True}},
                required=False,
            ),
        ]

    if args.deep and not run_id:
        print("Skipping deep checks: no run_id available.")

    if deep_cases:
        print("\n== Deep checks ==")
        for case in deep_cases:
            payload = await _run_case(case, token_provider, args.timeout_seconds)
            results.append(payload)
            status = "PASS" if payload.get("success") else "FAIL"
            print(f"[{status}] {payload['name']}: {payload.get('message')}")
            if payload.get("data") is not None:
                print(f"  data: {_fmt(payload.get('data'))}")
            if payload.get("error"):
                print(f"  error: {payload.get('error')}")

    if args.exercise_create:
        print("\n== Optional write check ==")
        attrs = await generate_attributes_levels(
            {"why_prompt": "What factors influence EV purchases?", "country": "United States"},
            token_provider,
        )
        print(
            f"[{'PASS' if attrs.success else 'FAIL'}] generate_attributes_levels: {attrs.message}"
        )
        if attrs.success:
            created = await create_experiment(
                {
                    "why_prompt": "What factors influence EV purchases?",
                    "country": "United States",
                    "pre_cooked_attributes_and_levels_lookup": attrs.data.get("attributes_levels", [])[:4],
                },
                token_provider,
            )
            print(f"[{'PASS' if created.success else 'FAIL'}] create_experiment: {created.message}")
            results.append(
                {
                    "name": "create_experiment",
                    "success": created.success,
                    "required": False,
                    "error": created.error,
                    "message": created.message,
                }
            )

    required_failures = [r for r in results if r.get("required") and not r.get("success")]
    optional_failures = [r for r in results if not r.get("required") and not r.get("success")]
    print("\n== Summary ==")
    print(f"required_failures={len(required_failures)} optional_failures={len(optional_failures)}")
    if required_failures:
        for item in required_failures:
            print(f"- required fail: {item['name']} error={item.get('error')} msg={item.get('message')}")
    if optional_failures:
        for item in optional_failures:
            print(f"- optional fail: {item['name']} error={item.get('error')} msg={item.get('message')}")

    return 1 if required_failures else 0


if __name__ == "__main__":
    try:
        raise SystemExit(asyncio.run(main()))
    except KeyboardInterrupt:
        sys.exit(130)
