# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Subconscious AI MCP Server - A Model Context Protocol (MCP) server that enables AI assistants (Claude, Cursor) to run AI-powered conjoint experiments via the Subconscious AI platform. Requires Python >= 3.11.

## Build and Development Commands

```bash
# Setup
python3 -m venv venv && source venv/bin/activate
pip install -e ".[dev]"          # install with dev deps (pytest, ruff, mypy)
# or: pip install -r requirements.txt  # runtime deps only

# Run local MCP server (stdio mode)
AUTH0_JWT_TOKEN="your_token" python server/main.py

# Run tests
pytest tests/ -v

# Run single test
pytest tests/test_handlers.py::TestCheckCausality::test_causal_question_returns_success -v

# Linting (both server and tests)
ruff check server/ tests/

# Type checking
mypy server/ --ignore-missing-imports

# Deploy to Vercel
vercel --prod

# Smoke test against live backend
AUTH0_JWT_TOKEN=... python scripts/smoke_mcp.py
python scripts/smoke_mcp.py --deep --run-id <run_id>

# Full E2E: create experiment, poll, download artifacts
AUTH0_JWT_TOKEN=... python scripts/run_e2e_download_artifacts.py
```

## Architecture

The server has two deployment modes with shared core logic:

### Core Module (`server/tools/_core/`)

Shared implementations used by both deployment modes:

- `base.py` - `ToolResult` dataclass, `TokenProvider` protocol, `EnvironmentTokenProvider`, `RequestTokenProvider`
- `exceptions.py` - Custom exception hierarchy: `AuthenticationError`, `AuthorizationError`, `NotFoundError`, `ValidationError`, `RateLimitError`, `ServerError`, `NetworkError`
- `handlers.py` - 15 unified async handler functions with proper error handling and logging
- `retry.py` - `@with_retry` decorator with exponential backoff for transient failures

### 1. Local Mode (`server/main.py`)
- Uses MCP stdio transport for direct integration with MCP clients
- Tools defined in `server/tools/` modules with `*_tool()` factory functions
- Handlers delegate to `_core/handlers.py` via `EnvironmentTokenProvider`

### 2. Remote/Hosted Mode (`api/index.py`)
- Vercel serverless deployment using Starlette + SSE
- MCP protocol: `GET /api/sse` (streaming), `POST /api/sse/message` (JSON-RPC)
- REST API: `POST /api/call/{tool_name}`, `GET /api/tools`, `GET /api/health`
- Auth: `Authorization: Bearer TOKEN` header only; query-string tokens are rejected
- Status: experimental until the hosted protocol and auth flow has a credentialed smoke test
- Uses `RequestTokenProvider` for per-request token handling

### Tool Organization (`server/tools/`)
- `ideation.py` - `check_causality`, `generate_attributes_levels` (run first)
- `population.py` - `validate_population`, `get_population_stats`
- `experiments.py` - `create_experiment`, `get_experiment_status`, `get_experiment_results`, `list_experiments`
- `runs.py` - `get_run_details`, `get_run_artifacts`, `update_run_config`
- `personas.py` - `generate_personas`, `get_experiment_personas`
- `analytics.py` - `get_amce_data`, `get_causal_insights`

### Utilities
- `server/utils/api_client.py` - `APIClient` HTTP wrapper (httpx-based)
- `server/config.py` - `MCPConfig` class, environment variable loading

### Experiment Workflow
1. `check_causality` - Validate research question is causal
2. `generate_attributes_levels` - Create experiment attributes/levels
3. `validate_population` (optional) - Check target population size
4. `create_experiment` - Run the experiment
5. `get_experiment_status` - Track progress
6. `get_experiment_results` - Get results when complete

## Testing

Tests use `pytest` + `pytest-asyncio` with `asyncio_mode = "auto"`. Tests are class-based.

| File | Coverage |
|---|---|
| `test_tools.py` | Tool schema validation, config loading, API client init |
| `test_handlers.py` | All 15 handlers with mocked HTTP, parametrized error mapping |
| `test_exceptions.py` | Exception hierarchy |
| `test_retry.py` | Retry decorator (success, transient retries, max exceeded, non-retryable) |
| `test_integration.py` | REST API endpoints via `httpx.ASGITransport` |
| `test_api_handler_parity.py` | REST API and MCP JSON-RPC match core handler output |

Key test patterns:
- Mock HTTP: `unittest.mock.patch("server.tools._core.handlers._api_request")`
- Integration: `httpx.ASGITransport` + `AsyncClient` against the Starlette app
- Fixtures in `tests/conftest.py`: `mock_token_provider`, `mock_api_response`, `sample_experiment_response`, `sample_run_response`, `sample_attributes_response`

## Error Handling

All handlers return `ToolResult` with structured error information:
- `success: bool` - Whether the operation succeeded
- `data: dict` - Response data on success
- `error: str` - Error type code on failure (e.g., `auth_error`, `rate_limit`)
- `message: str` - Human-readable message

Retry logic (`@with_retry`) automatically retries on `RateLimitError`, `ServerError`, and `NetworkError`. Does NOT retry on `AuthenticationError`, `AuthorizationError`, `NotFoundError`, `ValidationError`.

## CI/CD (.github/workflows/ci.yml)

Triggers on push/PR to `main` and `develop`. Three jobs on Ubuntu, Python 3.11:

1. **lint** - Ruff checks the server, hosted API, export/smoke scripts, and
   tests; mypy checks the server.
2. **test** - Runs all tests with full Git history because provenance tests
   read the exact tool-owning commit.
3. **validate-mcp** - Regenerates and rejects drift in
   `mcp-tools.public.json`, performs a real MCP `initialize` plus `tools/list`
   exchange, and uploads the exact public contract.

A squash merge changes the owning commit ID. Regenerate the checked manifest on
the merged lineage before treating `main` as green. The export may have
identical tool bytes while the provenance revision still needs to change.

## Scripts

- `scripts/smoke_mcp.py` - Smoke test handlers against live backend (use `--deep --run-id` for full coverage)
- `scripts/smoke_stdio_mcp.py` - Protocol-level `initialize` and `tools/list` proof for the supported local transport
- `scripts/export_mcp_manifest.py` - Deterministic export of the registry-owned public tool contract
- `scripts/run_e2e_download_artifacts.py` - Full E2E: create experiment, poll to completion, download artifacts to `artifacts/`

## Environment Variables

- `AUTH0_JWT_TOKEN` - Required. Get from app.subconscious.ai Settings (see `.env.example`)
- `API_BASE_URL` - Backend API (default: `https://api.subconscious.ai`, dev: `https://api.dev.subconscious.ai`)
- `SUBCONSCIOUSAI_M2M_CLIENT_ID` / `SUBCONSCIOUSAI_M2M_CLIENT_SECRET` - M2M client credentials (takes priority over JWT)
- `AUTH0_DOMAIN`, `AUTH0_AUDIENCE`, `AUTH0_CLIENT_ID`, `AUTH0_CLIENT_SECRET` - Auth0 OAuth config
- `CORS_ALLOWED_ORIGINS` - Comma-separated list of allowed CORS origins
- `CORS_ALLOW_ALL` - Set to `true` to allow all origins (development only)

## Conventions

Repository conventions:
- `snake_case` for functions/variables/files, `PascalCase` for classes
- `*_tool` suffix for tool factory functions, `handle_*` prefix for handlers
- Tests: `tests/test_<area>.py`, class-based, add success + failure tests per handler
- Never commit `AUTH0_JWT_TOKEN`; use `Authorization: Bearer` not query param tokens
- Ruff config: `line-length = 100`, rules E/F/I/N/W
