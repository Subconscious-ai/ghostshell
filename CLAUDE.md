# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Subconscious AI MCP Server - A Model Context Protocol (MCP) server that enables AI assistants (Claude, Cursor) to run AI-powered conjoint experiments via the Subconscious AI platform.

## Build and Development Commands

```bash
# Setup
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Run local MCP server (stdio mode)
AUTH0_JWT_TOKEN="your_token" python server/main.py

# Run tests
pytest tests/ -v

# Run single test
pytest tests/test_handlers.py::TestCheckCausality::test_causal_question_returns_success -v

# Linting
ruff check server/

# Type checking
mypy server/ --ignore-missing-imports

# Deploy to Vercel
vercel --prod
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
- Vercel serverless deployment using Starlette
- Exposes MCP protocol over SSE at `/api/sse`
- Also provides REST API at `/api/call/{tool_name}`
- Uses `RequestTokenProvider` for per-request token handling

### Tool Organization (`server/tools/`)
- `ideation.py` - `check_causality`, `generate_attributes_levels` (run first)
- `population.py` - `validate_population`, `get_population_stats`
- `experiments.py` - `create_experiment`, `get_experiment_status`, `get_experiment_results`, `list_experiments`
- `runs.py` - `get_run_details`, `get_run_artifacts`, `update_run_config`
- `personas.py` - `generate_personas`, `get_experiment_personas`
- `analytics.py` - `get_amce_data`, `get_causal_insights`

### Experiment Workflow
1. `check_causality` - Validate research question is causal
2. `generate_attributes_levels` - Create experiment attributes/levels
3. `validate_population` (optional) - Check target population size
4. `create_experiment` - Run the experiment
5. `get_experiment_status` - Track progress
6. `get_experiment_results` - Get results when complete

## Error Handling

All handlers return `ToolResult` with structured error information:
- `success: bool` - Whether the operation succeeded
- `data: dict` - Response data on success
- `error: str` - Error type code on failure (e.g., `auth_error`, `rate_limit`)
- `message: str` - Human-readable message

Retry logic automatically retries on `RateLimitError`, `ServerError`, and `NetworkError`.

## Environment Variables

- `AUTH0_JWT_TOKEN` - Required. Get from app.subconscious.ai Settings
- `API_BASE_URL` - Backend API (default: `https://api.subconscious.ai`, dev: `https://api.dev.subconscious.ai`)
- `CORS_ALLOWED_ORIGINS` - Comma-separated list of allowed CORS origins
- `CORS_ALLOW_ALL` - Set to `true` to allow all origins (development only)
