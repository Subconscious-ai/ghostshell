# Repository Guidelines

## Project Structure & Module Organization
- `server/` contains the local MCP stdio server and shared tool modules.
- `server/tools/` groups tool definitions by domain (`ideation.py`, `experiments.py`, `population.py`, `runs.py`, `personas.py`, `analytics.py`).
- `server/tools/_core/` contains shared handler, retry, and exception logic used by both local and hosted modes.
- `api/index.py` is the Starlette/Vercel entrypoint for REST + SSE endpoints.
- `tests/` contains `pytest` suites (`test_*.py`) for unit and integration coverage.
- `examples/` provides MCP client config samples (`examples/local/config.json`, `examples/cursor/mcp.json`, `examples/claude/config.json`).

## Build, Test, and Development Commands
- `python3 -m venv venv && source venv/bin/activate`: create/activate local environment.
- `pip install -r requirements.txt`: install runtime + test dependencies.
- `AUTH0_JWT_TOKEN=... python server/main.py`: run MCP server in stdio mode locally.
- `pytest -v`: run all tests.
- `pytest tests/test_integration.py -v`: run a focused suite.
- `ruff check server tests`: lint Python code.
- `mypy server --ignore-missing-imports`: type-check core modules.
- `vercel --prod`: deploy hosted API/SSE server.

## Coding Style & Naming Conventions
- Python uses 4-space indentation and type hints on public functions.
- Ruff is configured with `line-length = 100`; keep imports sorted and remove unused symbols.
- Follow existing naming patterns: snake_case for functions/variables/files, PascalCase for classes, `*_tool`/`handle_*` for tool factories and handlers.
- Keep modules domain-focused (add tool logic to the matching file in `server/tools/`).

## Testing Guidelines
- Framework: `pytest` with `pytest-asyncio` (`asyncio_mode = auto`).
- Name tests as `tests/test_<area>.py` and test functions as `test_<behavior>`.
- For new or changed handlers/tools, add at least one success-path test and one failure-path test.
- No fixed coverage gate is configured; maintain or improve coverage for touched code.

## Commit & Pull Request Guidelines
- Use concise, imperative commit subjects; optional Conventional Commit prefixes are acceptable (e.g., `chore:`, `fix:`).
- Link PRs to issues using `Refs #<issue>` or `Closes #<issue>` in PR body.
- PRs should include: purpose, scope, test evidence (`pytest`, `ruff`, `mypy` output), and API/behavior changes.
- If endpoints or tool schemas change, include example request/response snippets.

## Security & Configuration Tips
- Never commit real tokens (`AUTH0_JWT_TOKEN`) or secrets.
- Prefer `Authorization: Bearer` headers for API calls; query-param tokens are deprecated.
- Use `API_BASE_URL` and CORS env vars for environment-specific behavior instead of hardcoding.
