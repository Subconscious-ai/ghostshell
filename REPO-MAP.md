This file is a merged representation of a subset of the codebase, containing specifically included files, combined into a single document by Repomix.
The content has been processed where content has been compressed (code blocks are separated by ⋮---- delimiter).

<file_summary>
This section contains a summary of this file.

<purpose>
This file contains a packed representation of a subset of the repository's contents that is considered the most important context.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.
</purpose>

<file_format>
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  - File path as an attribute
  - Full contents of the file
</file_format>

<usage_guidelines>
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.
</usage_guidelines>

<notes>
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Only files matching these patterns are included: server/**/*.py, api/**/*.py, scripts/**/*.py, tests/**/*.py, *.py, requirements*.txt, pyproject.toml
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Content has been compressed - code blocks are separated by ⋮---- delimiter
- Files are sorted by Git change count (files with more changes are at the bottom)
</notes>

</file_summary>

<directory_structure>
api/
  index.py
scripts/
  run_e2e_download_artifacts.py
  smoke_mcp.py
server/
  tools/
    _core/
      __init__.py
      base.py
      exceptions.py
      handlers.py
      retry.py
    __init__.py
    analytics.py
    experiments.py
    ideation.py
    personas.py
    population.py
    runs.py
  utils/
    __init__.py
    api_client.py
  __init__.py
  config.py
  main.py
tests/
  __init__.py
  conftest.py
  test_api_handler_parity.py
  test_exceptions.py
  test_handlers.py
  test_integration.py
  test_retry.py
  test_tools.py
pyproject.toml
requirements.txt
</directory_structure>

<files>
This section contains the contents of the repository's files.

<file path="scripts/run_e2e_download_artifacts.py">
#!/usr/bin/env python3
"""Run a full experiment via MCP handlers and download exposed analytics artifacts locally."""
⋮----
def _json_dump(path: Path, data: Any) -> None
⋮----
def _extract_run_id(create_data: Dict[str, Any]) -> str | None
⋮----
def _state_from_details(data: Dict[str, Any]) -> str
⋮----
run_details = data.get("run_details", {})
⋮----
state = run_details.get("run_state") or run_details.get("state") or run_details.get("status")
⋮----
def _collect_candidate_files(data: Any) -> set[str]
⋮----
found: set[str] = set()
⋮----
def walk(node: Any) -> None
⋮----
key = str(k).lower()
⋮----
downloaded: list[str] = []
headers = {"Authorization": f"Bearer {token}"}
file_names = sorted(_collect_candidate_files(artifact_payload))
⋮----
encoded = quote(file_name, safe="")
url = f"{base_url}/api/v1/runs/artifact/{encoded}"
⋮----
resp = await client.get(url, headers=headers)
⋮----
out = out_dir / "files" / file_name.replace("/", "_")
⋮----
content_type = resp.headers.get("content-type", "")
⋮----
# Fallback to the most common run-scoped artifact names if nothing found.
⋮----
fallback = [
⋮----
async def main() -> int
⋮----
parser = argparse.ArgumentParser(
⋮----
args = parser.parse_args()
⋮----
token = os.getenv("AUTH0_JWT_TOKEN", "")
⋮----
base_url = args.api_base_url or os.getenv("API_BASE_URL", "")
⋮----
ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
out_dir = Path("artifacts") / f"e2e_{ts}"
⋮----
tp = EnvironmentTokenProvider()
⋮----
run_id = args.run_id
⋮----
attrs_res = await generate_attributes_levels(
attrs_payload = attrs_res.to_dict()
⋮----
attrs = attrs_payload.get("data", {}).get("attributes_levels", [])
create_res = await create_experiment(
create_payload = create_res.to_dict()
⋮----
run_id = _extract_run_id(create_payload.get("data", {}))
⋮----
started = time.monotonic()
terminal = {"completed", "finished", "failed", "error", "cancelled"}
state = "unknown"
details_payload: Dict[str, Any] = {}
⋮----
details_res = await get_run_details({"run_id": run_id}, tp)
details_payload = details_res.to_dict()
⋮----
state = _state_from_details(details_payload.get("data", {}))
elapsed = int(time.monotonic() - started)
⋮----
artifacts_res = await asyncio.wait_for(get_run_artifacts({"run_id": run_id}, tp), timeout=25)
artifacts_payload = artifacts_res.to_dict()
⋮----
artifacts_payload = {
⋮----
# Merge in run_details-derived file names as a reliable source for downloads.
detail_files = []
run_details = details_payload.get("data", {}).get("run_details", {})
⋮----
raw_files = run_details.get("files", [])
⋮----
detail_files = raw_files
merged_payload = {"artifact_payload": artifacts_payload.get("data"), "run_files": detail_files}
⋮----
downloaded = await _download_known_files(
</file>

<file path="scripts/smoke_mcp.py">
#!/usr/bin/env python3
"""Smoke test MCP core handlers against configured backend."""
⋮----
Handler = Callable[[Dict[str, Any], EnvironmentTokenProvider], Any]
⋮----
@dataclass
class SmokeCase
⋮----
name: str
handler: Handler
args: Dict[str, Any]
required: bool = True
⋮----
def _fmt(data: Any, max_len: int = 220) -> str
⋮----
text = json.dumps(data, default=str)
⋮----
result = await asyncio.wait_for(
payload = result.to_dict()
⋮----
payload = {
⋮----
def _extract_first_run_id(list_result: Dict[str, Any]) -> Optional[str]
⋮----
data = list_result.get("data", {})
runs = data.get("runs", []) if isinstance(data, dict) else []
⋮----
first = runs[0]
⋮----
async def main() -> int
⋮----
parser = argparse.ArgumentParser(description="Smoke test MCP handlers against backend API.")
⋮----
args = parser.parse_args()
⋮----
api_base_url = os.getenv("API_BASE_URL", "")
token = os.getenv("AUTH0_JWT_TOKEN", "")
⋮----
token_provider = EnvironmentTokenProvider()
cases: list[SmokeCase] = [
⋮----
results: list[Dict[str, Any]] = []
⋮----
payload = await _run_case(case, token_provider, args.timeout_seconds)
⋮----
status = "PASS" if payload.get("success") else "FAIL"
⋮----
list_result = next((r for r in results if r["name"] == "list_experiments"), {})
run_id = args.run_id or _extract_first_run_id(list_result)
⋮----
deep_cases: list[SmokeCase] = []
⋮----
deep_cases = [
⋮----
attrs = await generate_attributes_levels(
⋮----
created = await create_experiment(
⋮----
required_failures = [r for r in results if r.get("required") and not r.get("success")]
optional_failures = [r for r in results if not r.get("required") and not r.get("success")]
</file>

<file path="tests/test_api_handler_parity.py">
"""Parity tests between hosted API dispatch and shared core handlers."""
⋮----
@pytest.fixture
def client()
⋮----
"""Create test client."""
⋮----
transport = ASGITransport(app=app)
⋮----
class TestHostedParity
⋮----
"""Ensure hosted API uses the same behavior as shared handlers."""
⋮----
@pytest.mark.asyncio
    async def test_rest_tool_call_matches_core_success(self, client)
⋮----
"""REST call should match core handler output on success."""
arguments = {"why_prompt": "What influences EV adoption?"}
token = "test-token"
⋮----
expected = (
⋮----
response = await client.post(
⋮----
@pytest.mark.asyncio
    async def test_rest_tool_call_matches_core_error(self, client)
⋮----
"""REST call should match core handler output on errors."""
⋮----
@pytest.mark.asyncio
    async def test_mcp_tools_call_matches_core(self)
⋮----
"""MCP JSON-RPC tools/call should emit the same structured result."""
⋮----
msg_id = "1"
⋮----
response = await handle_mcp_request(
⋮----
payload = response["result"]["content"][0]["text"]
</file>

<file path="server/tools/_core/__init__.py">
"""Core shared implementations for MCP tools."""
⋮----
__all__ = [
⋮----
# Base types
⋮----
# Exceptions
⋮----
# Handlers
</file>

<file path="server/tools/_core/exceptions.py">
"""Custom exceptions for Subconscious AI API errors."""
⋮----
class SubconsciousError(Exception)
⋮----
"""Base exception for all Subconscious AI errors."""
⋮----
class AuthenticationError(SubconsciousError)
⋮----
"""Token invalid or expired (HTTP 401)."""
⋮----
class AuthorizationError(SubconsciousError)
⋮----
"""Access denied to resource (HTTP 403)."""
⋮----
class NotFoundError(SubconsciousError)
⋮----
"""Resource not found (HTTP 404)."""
⋮----
class ValidationError(SubconsciousError)
⋮----
"""Invalid request parameters (HTTP 400, 422)."""
⋮----
class RateLimitError(SubconsciousError)
⋮----
"""Rate limit exceeded (HTTP 429)."""
⋮----
class ServerError(SubconsciousError)
⋮----
"""Backend server error (HTTP 5xx)."""
⋮----
class NetworkError(SubconsciousError)
⋮----
"""Network connectivity or timeout issue."""
</file>

<file path="server/utils/__init__.py">
"""Utility modules for MCP server."""
⋮----
__all__ = ["APIClient"]
</file>

<file path="server/__init__.py">
"""MCP server for Subconscious AI API."""
⋮----
__version__ = "1.0.0"
</file>

<file path="tests/__init__.py">
"""Tests for Subconscious AI MCP Toolkit."""
</file>

<file path="tests/conftest.py">
"""Pytest fixtures for MCP server tests."""
⋮----
@pytest.fixture
def mock_token_provider()
⋮----
"""Mock token provider for testing."""
⋮----
provider = MagicMock(spec=TokenProvider)
⋮----
@pytest.fixture
def mock_api_response()
⋮----
"""Factory for mock API responses."""
⋮----
def _factory(status_code: int = 200, json_data: dict = None)
⋮----
response = AsyncMock()
⋮----
@pytest.fixture
def sample_experiment_response()
⋮----
"""Sample experiment creation response."""
⋮----
@pytest.fixture
def sample_run_response()
⋮----
"""Sample run details response."""
⋮----
@pytest.fixture
def sample_attributes_response()
⋮----
"""Sample attributes and levels response."""
</file>

<file path="tests/test_exceptions.py">
"""Tests for custom exceptions."""
⋮----
class TestExceptionHierarchy
⋮----
"""Tests for exception class hierarchy."""
⋮----
def test_all_exceptions_inherit_from_base(self)
⋮----
"""Test that all exceptions inherit from SubconsciousError."""
⋮----
def test_exceptions_can_be_raised_with_message(self)
⋮----
"""Test that exceptions can be raised with custom messages."""
⋮----
def test_base_exception_is_catchable(self)
⋮----
"""Test that SubconsciousError can catch all child exceptions."""
⋮----
exceptions_to_test = [
⋮----
pass  # Should catch all
</file>

<file path="tests/test_handlers.py">
"""Tests for tool handlers."""
⋮----
class TestCheckCausality
⋮----
"""Tests for check_causality handler."""
⋮----
@pytest.mark.asyncio
    async def test_causal_question_returns_success(self, mock_token_provider)
⋮----
"""Test that causal questions return success."""
⋮----
result = await check_causality(
⋮----
@pytest.mark.asyncio
    async def test_non_causal_question_returns_suggestions(self, mock_token_provider)
⋮----
"""Test that non-causal questions return suggestions."""
⋮----
@pytest.mark.asyncio
    async def test_authentication_error_handled(self, mock_token_provider)
⋮----
"""Test that authentication errors are handled properly."""
⋮----
class TestGenerateAttributesLevels
⋮----
"""Tests for generate_attributes_levels handler."""
⋮----
"""Test successful attribute generation."""
⋮----
result = await generate_attributes_levels(
⋮----
class TestCreateExperiment
⋮----
"""Tests for create_experiment handler."""
⋮----
"""Test successful experiment creation."""
⋮----
result = await create_experiment(
⋮----
@pytest.mark.asyncio
    async def test_handles_pre_cooked_attributes(self, mock_token_provider)
⋮----
"""Test handling of pre-cooked attributes."""
⋮----
pre_cooked = [
⋮----
# Verify the API was called with formatted attributes
call_args = mock_request.call_args
payload = call_args[0][3]  # Fourth argument is json_data
⋮----
class TestListExperiments
⋮----
"""Tests for list_experiments handler."""
⋮----
@pytest.mark.asyncio
    async def test_lists_experiments_successfully(self, mock_token_provider)
⋮----
"""Test successful experiment listing."""
⋮----
result = await list_experiments({"limit": 10}, mock_token_provider)
⋮----
@pytest.mark.asyncio
    async def test_respects_limit_parameter(self, mock_token_provider)
⋮----
"""Test that limit parameter is respected."""
⋮----
result = await list_experiments({"limit": 3}, mock_token_provider)
⋮----
class TestGetExperimentStatus
⋮----
"""Tests for get_experiment_status handler."""
⋮----
"""Test successful status retrieval."""
⋮----
result = await get_experiment_status(
⋮----
class TestGetCausalInsights
⋮----
"""Tests for get_causal_insights handler."""
⋮----
@pytest.mark.asyncio
    async def test_gets_insights_successfully(self, mock_token_provider)
⋮----
"""Test successful insights retrieval."""
⋮----
result = await get_causal_insights(
⋮----
class TestRemainingHandlers
⋮----
"""Additional coverage for handlers not exercised above."""
⋮----
@pytest.mark.asyncio
    async def test_validate_population_success(self, mock_token_provider)
⋮----
"""Test successful population validation."""
⋮----
result = await validate_population({}, mock_token_provider)
⋮----
@pytest.mark.asyncio
    async def test_get_population_stats_success(self, mock_token_provider)
⋮----
"""Test successful population stats retrieval."""
⋮----
result = await get_population_stats({}, mock_token_provider)
⋮----
"""Test successful experiment results retrieval."""
⋮----
result = await get_experiment_results(
⋮----
@pytest.mark.asyncio
    async def test_get_run_details_success(self, mock_token_provider)
⋮----
"""Test successful run details retrieval."""
⋮----
result = await get_run_details({"run_id": "run-1"}, mock_token_provider)
⋮----
@pytest.mark.asyncio
    async def test_get_run_artifacts_success(self, mock_token_provider)
⋮----
"""Test successful run artifacts retrieval."""
⋮----
result = await get_run_artifacts({"run_id": "run-1"}, mock_token_provider)
⋮----
@pytest.mark.asyncio
    async def test_update_run_config_success(self, mock_token_provider)
⋮----
"""Test successful run config update."""
⋮----
result = await update_run_config(
⋮----
payload = call_args[0][3]
⋮----
@pytest.mark.asyncio
    async def test_generate_personas_success(self, mock_token_provider)
⋮----
"""Test successful persona generation."""
⋮----
result = await generate_personas(
⋮----
@pytest.mark.asyncio
    async def test_get_experiment_personas_success(self, mock_token_provider)
⋮----
"""Test successful persona retrieval."""
⋮----
result = await get_experiment_personas(
⋮----
@pytest.mark.asyncio
    async def test_get_amce_data_success(self, mock_token_provider)
⋮----
"""Test successful AMCE data retrieval."""
⋮----
result = await get_amce_data({"run_id": "run-1"}, mock_token_provider)
⋮----
class TestErrorMappingCoverage
⋮----
"""Ensure every handler maps auth failures consistently."""
⋮----
"""Every handler should return standardized auth errors."""
⋮----
handler = getattr(handlers, handler_name)
⋮----
result = await handler(arguments, mock_token_provider)
</file>

<file path="tests/test_retry.py">
"""Tests for retry decorator."""
⋮----
class TestRetryDecorator
⋮----
"""Tests for the retry decorator."""
⋮----
@pytest.mark.asyncio
    async def test_successful_call_no_retry(self)
⋮----
"""Test that successful calls don't retry."""
⋮----
mock_func = AsyncMock(return_value="success")
decorated = with_retry(max_retries=3)(mock_func)
⋮----
result = await decorated()
⋮----
@pytest.mark.asyncio
    async def test_retry_on_server_error(self)
⋮----
"""Test that server errors trigger retries."""
⋮----
mock_func = AsyncMock(
decorated = with_retry(max_retries=3, base_delay=0.01)(mock_func)
⋮----
@pytest.mark.asyncio
    async def test_retry_on_network_error(self)
⋮----
"""Test that network errors trigger retries."""
⋮----
mock_func = AsyncMock(side_effect=[NetworkError("timeout"), "success"])
⋮----
@pytest.mark.asyncio
    async def test_retry_on_rate_limit_error(self)
⋮----
"""Test that rate limit errors trigger retries."""
⋮----
mock_func = AsyncMock(side_effect=[RateLimitError("429"), "success"])
⋮----
@pytest.mark.asyncio
    async def test_max_retries_exceeded_raises(self)
⋮----
"""Test that exceeding max retries raises the exception."""
⋮----
mock_func = AsyncMock(side_effect=NetworkError("timeout"))
decorated = with_retry(max_retries=2, base_delay=0.01)(mock_func)
⋮----
assert mock_func.call_count == 3  # Initial + 2 retries
⋮----
@pytest.mark.asyncio
    async def test_no_retry_on_auth_error(self)
⋮----
"""Test that authentication errors don't trigger retries."""
⋮----
mock_func = AsyncMock(side_effect=AuthenticationError("invalid token"))
⋮----
# Should not retry on auth errors
⋮----
@pytest.mark.asyncio
    async def test_no_retry_on_validation_error(self)
⋮----
"""Test that validation errors don't trigger retries."""
⋮----
mock_func = AsyncMock(side_effect=ValidationError("bad input"))
⋮----
# Should not retry on validation errors
</file>

<file path="pyproject.toml">
[project]
name = "subconscious-ai-mcp"
version = "1.0.0"
description = "MCP server for Subconscious AI API"
readme = "README.md"
requires-python = ">=3.11"
license = {text = "Proprietary"}
authors = [
    {name = "Nihar Shah", email = "nihar@subconscious.ai"}
]
keywords = ["mcp", "ai", "conjoint", "experiments"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: Other/Proprietary License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
]
dependencies = [
    "mcp>=1.0.0",
    "httpx>=0.25.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "python-dotenv>=1.0.0",
    "starlette>=0.30.0",
    "uvicorn>=0.24.0",
    "sse-starlette>=1.6.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
]

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["."]
include = ["server*"]

[tool.ruff]
target-version = "py310"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W"]
ignore = ["E501"]

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_ignores = true
ignore_missing_imports = true

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
</file>

<file path="server/tools/_core/base.py">
"""Base types and protocols for tool handlers."""
⋮----
@dataclass
class ToolResult
⋮----
"""Standardized tool result."""
⋮----
success: bool
data: Optional[Dict[str, Any]] = None
error: Optional[str] = None
message: Optional[str] = None
⋮----
def to_dict(self) -> Dict[str, Any]
⋮----
"""Convert to dictionary for JSON serialization."""
result: Dict[str, Any] = {"success": self.success}
⋮----
class TokenProvider(Protocol)
⋮----
"""Protocol for token retrieval strategies."""
⋮----
def get_token(self) -> str
⋮----
"""Get the authentication token."""
⋮----
class EnvironmentTokenProvider
⋮----
"""Get token from environment variable (local mode)."""
⋮----
"""Get token from environment."""
⋮----
class RequestTokenProvider
⋮----
"""Get token from request (remote/SSE mode)."""
⋮----
def __init__(self, token: str)
⋮----
"""Initialize with token from request."""
⋮----
"""Return the stored token."""
</file>

<file path="server/tools/_core/retry.py">
"""Retry decorator with exponential backoff."""
⋮----
logger = logging.getLogger("subconscious-ai")
⋮----
T = TypeVar("T")
P = ParamSpec("P")
⋮----
# Exceptions that should trigger a retry
RETRYABLE_ERRORS: Tuple[Type[Exception], ...] = (
⋮----
"""
    Retry decorator with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay between retries in seconds
        exponential: Whether to use exponential backoff (2^attempt)

    Returns:
        Decorated async function with retry logic
    """
⋮----
def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]
⋮----
@wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T
⋮----
last_exception: Exception | None = None
⋮----
last_exception = e
⋮----
delay = base_delay * (2**attempt if exponential else 1)
⋮----
# If we get here, all retries failed
</file>

<file path="tests/test_integration.py">
"""Integration tests for API endpoints."""
⋮----
class TestAPIEndpoints
⋮----
"""Tests for the REST API endpoints."""
⋮----
@pytest.fixture
    def client(self)
⋮----
"""Create test client."""
⋮----
transport = ASGITransport(app=app)
⋮----
@pytest.mark.asyncio
    async def test_health_endpoint(self, client)
⋮----
"""Test health check endpoint."""
⋮----
response = await client.get("/api/health")
⋮----
data = response.json()
⋮----
@pytest.mark.asyncio
    async def test_server_info_endpoint(self, client)
⋮----
"""Test server info endpoint."""
⋮----
response = await client.get("/")
⋮----
@pytest.mark.asyncio
    async def test_tools_list_endpoint(self, client)
⋮----
"""Test tools listing endpoint."""
⋮----
response = await client.get("/api/tools")
⋮----
tool_names = [t["name"] for t in data["tools"]]
⋮----
@pytest.mark.asyncio
    async def test_call_tool_without_auth_returns_401(self, client)
⋮----
"""Test that calling a tool without auth returns 401."""
⋮----
response = await client.post(
⋮----
@pytest.mark.asyncio
    async def test_call_unknown_tool_returns_404(self, client)
⋮----
"""Test that calling unknown tool returns 404."""
⋮----
@pytest.mark.asyncio
    async def test_sse_endpoint_without_token_returns_401(self, client)
⋮----
"""Test that SSE endpoint requires token."""
⋮----
response = await client.get("/api/sse")
⋮----
class TestToolSchemas
⋮----
"""Tests for tool input schemas."""
⋮----
@pytest.mark.asyncio
    async def test_check_causality_schema(self, client)
⋮----
"""Test check_causality tool schema."""
⋮----
tools = {t["name"]: t for t in response.json()["tools"]}
⋮----
schema = tools["check_causality"]["inputSchema"]
⋮----
@pytest.mark.asyncio
    async def test_create_experiment_schema(self, client)
⋮----
"""Test create_experiment tool schema."""
⋮----
schema = tools["create_experiment"]["inputSchema"]
⋮----
@pytest.mark.asyncio
    async def test_all_tools_have_valid_schemas(self, client)
⋮----
"""Test that all tools have valid schemas."""
⋮----
tools = response.json()["tools"]
</file>

<file path="requirements.txt">
# Subconscious AI MCP Toolkit - Unified Requirements
# Install with: pip install -r requirements.txt

# Core MCP dependencies
mcp>=1.0.0

# HTTP client (async)
httpx>=0.25.0

# Configuration and validation
pydantic>=2.0.0
pydantic-settings>=2.0.0
python-dotenv>=1.0.0

# Web server (for SSE transport / Vercel deployment)
starlette>=0.30.0
uvicorn>=0.24.0
sse-starlette>=1.6.0
</file>

<file path="server/tools/_core/handlers.py">
"""Unified tool handlers shared between local and remote modes."""
⋮----
logger = logging.getLogger("subconscious-ai")
⋮----
# Configuration
API_BASE_URL = config.api_base_url
REQUEST_TIMEOUT = config.request_timeout
MAX_RETRIES = config.max_retries
RETRY_DELAY = config.retry_delay
⋮----
# =============================================================================
# API Request Helper
⋮----
"""
    Make authenticated API request to Subconscious AI backend.

    Args:
        method: HTTP method (GET, POST)
        endpoint: API endpoint path
        token_provider: Provider for authentication token
        json_data: Optional JSON payload for POST requests

    Returns:
        Parsed JSON response

    Raises:
        AuthenticationError: Token invalid or expired (401)
        AuthorizationError: Access denied (403)
        NotFoundError: Resource not found (404)
        ValidationError: Invalid request (400, 422)
        RateLimitError: Rate limit exceeded (429)
        ServerError: Backend error (5xx)
        NetworkError: Connection or timeout issue
    """
token = token_provider.get_token()
headers = {
url = f"{API_BASE_URL}{endpoint}"
⋮----
response = await client.get(url, headers=headers)
⋮----
response = await client.post(url, headers=headers, json=json_data or {})
⋮----
response = await client.put(url, headers=headers, json=json_data or {})
⋮----
# Map status codes to specific exceptions
⋮----
error_detail = response.json().get("detail", "Invalid request")
⋮----
error_detail = response.text or "Invalid request"
⋮----
# Catch-all for unhandled 4xx errors (e.g., 409 Conflict, 408 Timeout)
⋮----
def _handle_error(e: Exception, operation: str) -> ToolResult
⋮----
"""Convert exception to ToolResult with appropriate message."""
⋮----
# Ideation Tools
⋮----
"""Check if a research question is causal."""
model_map = {"sonnet": "databricks-claude-sonnet-4", "gpt4": "azure-openai-gpt4"}
llm_model = model_map.get(
⋮----
response = await _api_request(
is_causal = response.get("is_causal", False)
⋮----
"""Generate attributes and levels for a conjoint experiment."""
⋮----
attrs = (
⋮----
# Population Tools
⋮----
"""Validate target population demographics."""
country = args.get("country", "United States of America (USA)")
⋮----
target_population = args.get("target_population", {}) or {}
# Keep backward compatibility with existing MCP payload shape while matching
# rehoboam's /api/v1/populations/validate schema.
payload: Dict[str, Any] = {
payload = {k: v for k, v in payload.items() if v is not None}
⋮----
"""Get population statistics for a country."""
⋮----
# Rehoboam does not expose /population/stats; use validate with defaults.
⋮----
# Experiment Tools
⋮----
"""Create and run a conjoint experiment."""
⋮----
country = args.get("country", "United States")
⋮----
country = "United States of America (USA)"
⋮----
payload = {
⋮----
# Handle pre-cooked attributes
⋮----
raw_attrs = args["pre_cooked_attributes_and_levels_lookup"]
formatted = []
⋮----
run_id = response.get("run_id", response.get("id", "unknown"))
⋮----
"""Check experiment status."""
⋮----
status = response.get("status", "unknown")
⋮----
"""Get experiment results."""
⋮----
"""List all experiments."""
⋮----
runs = (
limit = args.get("limit", 20)
runs = runs[:limit]
⋮----
# Run Tools
⋮----
"""Get detailed run information."""
⋮----
"""Get run artifacts and files."""
⋮----
"""Update run configuration."""
config_payload = args.get("config", {}) or {}
⋮----
config_payload = {**config_payload, "set_privacy": config_payload["toggle_privacy"]}
⋮----
# Persona Tools
⋮----
"""Generate AI personas for experiment."""
⋮----
count = args.get("count", 5)
⋮----
personas = response.get("personas", [])
limited = personas[:count]
data: Any = {"personas": limited, "total": len(limited), "run_id": args["run_id"]}
total = len(limited)
⋮----
data = response[:count]
total = len(data)
⋮----
data = response
total = count
⋮----
"""Get experiment personas."""
⋮----
# Analytics Tools
⋮----
"""Get AMCE (Average Marginal Component Effect) analytics data."""
⋮----
"""Get AI-generated causal insights."""
⋮----
sentences: list[str] = (
</file>

<file path="server/tools/__init__.py">
"""MCP tools for Subconscious AI API."""
⋮----
__all__ = [
⋮----
# Ideation (Step 1-2)
⋮----
# Population
⋮----
# Experiments
⋮----
# Runs
⋮----
# Personas
⋮----
# Analytics
</file>

<file path="server/utils/api_client.py">
"""HTTP client for Subconscious AI API."""
⋮----
class APIClient
⋮----
"""HTTP client for interacting with Subconscious AI API."""
⋮----
def __init__(self, base_url: Optional[str] = None)
⋮----
"""Initialize API client.

        Args:
            base_url: Optional API base URL override
        """
⋮----
def _get_headers(self) -> Dict[str, str]
⋮----
"""Get request headers with authentication."""
⋮----
"""Make HTTP request to API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments for httpx request

        Returns:
            JSON response data

        Raises:
            httpx.HTTPError: If request fails
        """
url = f"{self.base_url}{endpoint}"
⋮----
# Update headers with auth token
headers = self._get_headers()
⋮----
response = await client.request(
⋮----
async def get(self, endpoint: str, **kwargs) -> Dict[str, Any]
⋮----
"""Make GET request."""
⋮----
async def post(self, endpoint: str, json: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]
⋮----
"""Make POST request."""
⋮----
async def put(self, endpoint: str, json: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]
⋮----
"""Make PUT request."""
⋮----
async def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]
⋮----
"""Make DELETE request."""
</file>

<file path="server/main.py">
#!/usr/bin/env python3
"""MCP server for Subconscious AI API.

Experiment Workflow:
1. check_causality - Validate research question is causal
2. generate_attributes_levels - Create experiment attributes/levels
3. validate_population (optional) - Check target population size
4. create_experiment - Run the experiment
5. get_experiment_status - Track progress
6. get_experiment_results - Get results when complete
"""
⋮----
# Add parent directory to path for imports
⋮----
# Ideation (Step 1-2)
⋮----
# Experiments
⋮----
# Personas
⋮----
# Analytics
⋮----
# Runs
⋮----
# Population
⋮----
# Create MCP server instance
server = Server(config.server_name)
⋮----
@server.list_tools()
async def list_tools() -> list[Tool]
⋮----
"""List all available tools."""
⋮----
# Ideation workflow (run these first)
⋮----
# Population validation
⋮----
# Experiment management
⋮----
# Run details
⋮----
@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]
⋮----
"""Handle tool execution."""
handlers = {
⋮----
# Ideation
⋮----
handler = handlers.get(name)
⋮----
result = await handler(arguments)
⋮----
text = f"{result.get('message', 'Success')}\n\n{_format_result(result.get('data', {}))}"
⋮----
text = f"{result.get('message', 'Error')}: {result.get('error', 'Unknown error')}"
⋮----
def _format_result(data: dict) -> str
⋮----
"""Format result data for display."""
⋮----
async def main()
⋮----
"""Main entry point."""
</file>

<file path="server/tools/personas.py">
"""MCP tools for persona management."""
⋮----
def generate_personas_tool() -> MCPTool
⋮----
"""Generate synthetic personas for experiments."""
⋮----
async def handle_generate_personas(arguments: Dict[str, Any]) -> Dict[str, Any]
⋮----
"""Handle generate_personas tool execution."""
result = await _generate_personas(arguments, EnvironmentTokenProvider())
⋮----
def get_experiment_personas_tool() -> MCPTool
⋮----
"""Get personas from a completed experiment."""
⋮----
async def handle_get_experiment_personas(arguments: Dict[str, Any]) -> Dict[str, Any]
⋮----
"""Handle get_experiment_personas tool execution."""
result = await _get_experiment_personas(arguments, EnvironmentTokenProvider())
</file>

<file path="server/tools/population.py">
"""MCP tools for population management."""
⋮----
def validate_population_tool() -> MCPTool
⋮----
"""Validate population configuration."""
⋮----
async def handle_validate_population(arguments: Dict[str, Any]) -> Dict[str, Any]
⋮----
"""Handle validate_population tool execution."""
result = await _validate_population(arguments, EnvironmentTokenProvider())
⋮----
def get_population_stats_tool() -> MCPTool
⋮----
"""Get population statistics."""
⋮----
async def handle_get_population_stats(arguments: Dict[str, Any]) -> Dict[str, Any]
⋮----
"""Handle get_population_stats tool execution."""
result = await _get_population_stats(arguments, EnvironmentTokenProvider())
</file>

<file path="server/tools/runs.py">
"""MCP tools for run management."""
⋮----
def get_run_details_tool() -> MCPTool
⋮----
"""Get detailed information about a specific run."""
⋮----
async def handle_get_run_details(arguments: Dict[str, Any]) -> Dict[str, Any]
⋮----
"""Handle get_run_details tool execution."""
result = await _get_run_details(arguments, EnvironmentTokenProvider())
⋮----
def get_run_artifacts_tool() -> MCPTool
⋮----
"""Get run artifacts (CSV files, images, etc.)."""
⋮----
async def handle_get_run_artifacts(arguments: Dict[str, Any]) -> Dict[str, Any]
⋮----
"""Handle get_run_artifacts tool execution."""
result = await _get_run_artifacts(arguments, EnvironmentTokenProvider())
⋮----
def update_run_config_tool() -> MCPTool
⋮----
"""Update experiment run configuration."""
⋮----
async def handle_update_run_config(arguments: Dict[str, Any]) -> Dict[str, Any]
⋮----
"""Handle update_run_config tool execution."""
result = await _update_run_config(arguments, EnvironmentTokenProvider())
</file>

<file path="server/tools/analytics.py">
"""MCP tools for analytics and insights."""
⋮----
def get_amce_data_tool() -> MCPTool
⋮----
"""Get Average Marginal Component Effect (AMCE) data."""
⋮----
async def handle_get_amce_data(arguments: Dict[str, Any]) -> Dict[str, Any]
⋮----
"""Handle get_amce_data tool execution."""
result = await _get_amce_data(arguments, EnvironmentTokenProvider())
⋮----
def get_causal_insights_tool() -> MCPTool
⋮----
"""Get causal insights from experiment results."""
⋮----
async def handle_get_causal_insights(arguments: Dict[str, Any]) -> Dict[str, Any]
⋮----
"""Handle get_causal_insights tool execution."""
result = await _get_causal_insights(arguments, EnvironmentTokenProvider())
</file>

<file path="server/tools/experiments.py">
"""MCP tools for experiment management."""
⋮----
def create_experiment_tool() -> MCPTool
⋮----
"""Create and run a new conjoint experiment."""
⋮----
async def handle_create_experiment(arguments: Dict[str, Any]) -> Dict[str, Any]
⋮----
"""Handle create_experiment tool execution."""
result = await _create_experiment(arguments, EnvironmentTokenProvider())
⋮----
def get_experiment_status_tool() -> MCPTool
⋮----
"""Get experiment execution status."""
⋮----
async def handle_get_experiment_status(arguments: Dict[str, Any]) -> Dict[str, Any]
⋮----
"""Handle get_experiment_status tool execution."""
result = await _get_experiment_status(arguments, EnvironmentTokenProvider())
⋮----
def get_experiment_results_tool() -> MCPTool
⋮----
"""Get experiment results and analytics."""
⋮----
async def handle_get_experiment_results(arguments: Dict[str, Any]) -> Dict[str, Any]
⋮----
"""Handle get_experiment_results tool execution."""
result = await _get_experiment_results(arguments, EnvironmentTokenProvider())
⋮----
def list_experiments_tool() -> MCPTool
⋮----
"""List all user experiments."""
⋮----
async def handle_list_experiments(arguments: Dict[str, Any]) -> Dict[str, Any]
⋮----
"""Handle list_experiments tool execution."""
result = await _list_experiments(arguments, EnvironmentTokenProvider())
</file>

<file path="server/tools/ideation.py">
"""MCP tools for ideation workflow - causality check and attribute/level generation."""
⋮----
# =============================================================================
# STEP 1: Check Causality
⋮----
def check_causality_tool() -> MCPTool
⋮----
"""Check if a research question is causal."""
⋮----
async def handle_check_causality(arguments: Dict[str, Any]) -> Dict[str, Any]
⋮----
"""Handle check_causality tool execution."""
result = await _check_causality(arguments, EnvironmentTokenProvider())
⋮----
# STEP 2: Generate Attributes and Levels
⋮----
def generate_attributes_levels_tool() -> MCPTool
⋮----
"""Generate attributes and levels for a conjoint experiment."""
⋮----
async def handle_generate_attributes_levels(arguments: Dict[str, Any]) -> Dict[str, Any]
⋮----
"""Handle generate_attributes_levels tool execution."""
result = await _generate_attributes_levels(arguments, EnvironmentTokenProvider())
</file>

<file path="server/config.py">
"""Configuration management for MCP server."""
⋮----
# Load .env file
⋮----
# Configure logging
⋮----
logger = logging.getLogger("subconscious-ai")
⋮----
class MCPConfig
⋮----
"""MCP server configuration."""
⋮----
auth0_jwt_token: str | None
⋮----
def __init__(self)
⋮----
# Auth0 Configuration
⋮----
# Try M2M client credentials first, then fall back to regular
⋮----
# Direct JWT token (optional)
⋮----
# API Configuration
⋮----
# Server Configuration
⋮----
# Timeout Configuration
⋮----
# CORS Configuration
# Note: Starlette CORSMiddleware doesn't support wildcards in origins list.
# Use cors_origin_regex for pattern matching.
cors_origins_env = os.getenv("CORS_ALLOWED_ORIGINS", "")
cors_allow_all = os.getenv("CORS_ALLOW_ALL", "").lower() in ("true", "1", "yes")
⋮----
# Default: explicit production origins + regex for dev/preview
⋮----
# Regex to match Vercel preview deployments and localhost
⋮----
# Note: allow_credentials=True cannot be used with allow_origins=["*"] per CORS spec
⋮----
# Global configuration instance
config = MCPConfig()
⋮----
def get_auth_token() -> str
⋮----
"""Get Auth0 JWT token from environment."""
token: str | None = config.auth0_jwt_token
</file>

<file path="tests/test_tools.py">
"""Tests for MCP tools."""
⋮----
class TestToolDefinitions
⋮----
"""Test that tools are properly defined."""
⋮----
def test_check_causality_tool_definition(self)
⋮----
tool = check_causality_tool()
⋮----
def test_generate_attributes_levels_tool_definition(self)
⋮----
tool = generate_attributes_levels_tool()
⋮----
def test_create_experiment_tool_definition(self)
⋮----
tool = create_experiment_tool()
⋮----
def test_get_experiment_status_tool_definition(self)
⋮----
tool = get_experiment_status_tool()
⋮----
def test_list_experiments_tool_definition(self)
⋮----
tool = list_experiments_tool()
⋮----
class TestConfig
⋮----
"""Test configuration."""
⋮----
def test_config_loads(self)
⋮----
class TestAPIClient
⋮----
"""Test API client."""
⋮----
def test_api_client_init(self)
⋮----
client = APIClient()
# Should use env var if set, otherwise default to prod URL
expected = os.getenv("API_BASE_URL", "https://api.subconscious.ai")
⋮----
def test_api_client_custom_url(self)
⋮----
client = APIClient(base_url="https://custom.api.com")
</file>

<file path="api/index.py">
"""Subconscious AI MCP Server - Vercel Deployment.

Remote MCP server for AI assistants to run conjoint experiments.
Supports MCP protocol via SSE for Cursor/Claude Desktop integration.
"""
⋮----
logger = logging.getLogger("subconscious-ai")
⋮----
CoreHandler = Callable[[Dict[str, Any], RequestTokenProvider], Awaitable[ToolResult]]
⋮----
@dataclass(frozen=True)
class ToolSpec
⋮----
"""Hosted tool metadata + shared core handler binding."""
⋮----
handler: CoreHandler
description: str
input_schema: Dict[str, Any]
⋮----
# =============================================================================
# Authentication
⋮----
def extract_token(request: Request) -> Optional[str]
⋮----
"""Extract JWT token from Authorization header or query param.

    Note: Query param tokens are deprecated. Prefer Authorization header.
    """
auth_header = request.headers.get("Authorization", "")
⋮----
query_token = request.query_params.get("token")
⋮----
# Tool Registry
⋮----
def _build_tools() -> Dict[str, ToolSpec]
⋮----
"""Build tool registry from canonical MCP schemas and shared handlers."""
tool_specs: Dict[str, ToolSpec] = {}
definitions: list[tuple[Callable[[], Any], CoreHandler]] = [
⋮----
tool = tool_factory()
⋮----
TOOLS = _build_tools()
⋮----
def _list_tools_payload() -> list[Dict[str, Any]]
⋮----
"""List tool metadata for MCP and REST responses."""
⋮----
async def execute_tool(tool_name: str, arguments: Dict[str, Any], token: str) -> Dict[str, Any]
⋮----
"""Execute a tool via the shared core handler layer."""
spec = TOOLS[tool_name]
result = await spec.handler(arguments, RequestTokenProvider(token))
⋮----
# MCP Protocol over SSE
⋮----
SESSIONS: Dict[str, Dict[str, Any]] = {}
⋮----
async def handle_mcp_request(method: str, params: Dict[str, Any], msg_id: Any, token: str) -> Optional[Dict[str, Any]]
⋮----
"""Handle MCP JSON-RPC requests."""
⋮----
tool_name = params.get("name")
arguments = params.get("arguments", {})
⋮----
result = await execute_tool(tool_name, arguments, token)
⋮----
async def sse_endpoint(request: Request)
⋮----
"""SSE endpoint for MCP protocol - Cursor/Claude connect here."""
token = extract_token(request)
⋮----
session_id = str(uuid.uuid4())
⋮----
async def event_stream()
⋮----
response = await asyncio.wait_for(
⋮----
async def sse_message_endpoint(request: Request)
⋮----
"""Handle POST messages from MCP clients."""
session_id = request.query_params.get("session_id")
⋮----
session = SESSIONS[session_id]
⋮----
message = await request.json()
response = await handle_mcp_request(
⋮----
# REST API Endpoints
⋮----
async def health_check(request: Request) -> JSONResponse
⋮----
async def server_info(request: Request) -> JSONResponse
⋮----
async def list_tools_endpoint(request: Request) -> JSONResponse
⋮----
tools_list = _list_tools_payload()
⋮----
async def call_tool_endpoint(request: Request) -> JSONResponse
⋮----
tool_name = request.path_params.get("tool_name")
⋮----
body = await request.json()
⋮----
body = {}
⋮----
result = await execute_tool(tool_name, body, token)
⋮----
# Application
⋮----
_cors_config: Dict[str, Any] = {
⋮----
middleware = [Middleware(CORSMiddleware, **_cors_config)]
⋮----
app = Starlette(
</file>

</files>
