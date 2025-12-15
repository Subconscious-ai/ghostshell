"""Unified tool handlers shared between local and remote modes."""

import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional, cast
from urllib.parse import urlencode

import httpx

from .base import TokenProvider, ToolResult
from .exceptions import (
    AuthenticationError,
    AuthorizationError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from .retry import with_retry

logger = logging.getLogger("subconscious-ai")

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.subconscious.ai")
REQUEST_TIMEOUT = 300
MAX_RETRIES = 3
RETRY_DELAY = 1.0


# =============================================================================
# API Request Helper
# =============================================================================


@with_retry(max_retries=MAX_RETRIES, base_delay=RETRY_DELAY)
async def _api_request(
    method: str,
    endpoint: str,
    token_provider: TokenProvider,
    json_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
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
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    url = f"{API_BASE_URL}{endpoint}"

    logger.debug(f"API request: {method} {endpoint}")

    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            if method == "GET":
                response = await client.get(url, headers=headers)
            elif method == "POST":
                response = await client.post(url, headers=headers, json=json_data or {})
            elif method == "PUT":
                response = await client.put(url, headers=headers, json=json_data or {})
            else:
                raise ValueError(f"Unsupported method: {method}")

            logger.debug(f"API response: {response.status_code}")

            # Map status codes to specific exceptions
            if response.status_code == 401:
                raise AuthenticationError("Invalid or expired token")
            elif response.status_code == 403:
                raise AuthorizationError("Access denied to this resource")
            elif response.status_code == 404:
                raise NotFoundError(f"Resource not found: {endpoint}")
            elif response.status_code == 429:
                raise RateLimitError("Rate limit exceeded - try again later")
            elif response.status_code in (400, 422):
                try:
                    error_detail = response.json().get("detail", "Invalid request")
                except Exception:
                    error_detail = response.text or "Invalid request"
                raise ValidationError(str(error_detail))
            elif response.status_code >= 500:
                raise ServerError(f"Backend error: {response.status_code}")
            elif response.status_code >= 400:
                # Catch-all for unhandled 4xx errors (e.g., 409 Conflict, 408 Timeout)
                raise ValidationError(f"Request failed: {response.status_code}")

            response.raise_for_status()
            return cast(Dict[str, Any], response.json())

    except httpx.ConnectError as e:
        logger.error(f"Connection error: {e}")
        raise NetworkError("Cannot connect to API server")
    except httpx.TimeoutException as e:
        logger.error(f"Timeout error: {e}")
        raise NetworkError(f"Request timed out after {REQUEST_TIMEOUT}s")
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error: {e}")
        raise ServerError(f"Unexpected HTTP error: {e.response.status_code}")


def _handle_error(e: Exception, operation: str) -> ToolResult:
    """Convert exception to ToolResult with appropriate message."""
    if isinstance(e, AuthenticationError):
        return ToolResult(
            success=False,
            error="auth_error",
            message="Token invalid or expired. Please refresh your token.",
        )
    elif isinstance(e, AuthorizationError):
        return ToolResult(
            success=False,
            error="authorization_error",
            message="Access denied. You don't have permission for this resource.",
        )
    elif isinstance(e, NotFoundError):
        return ToolResult(
            success=False,
            error="not_found",
            message=f"Resource not found. {operation}",
        )
    elif isinstance(e, ValidationError):
        return ToolResult(
            success=False,
            error="validation_error",
            message=str(e),
        )
    elif isinstance(e, RateLimitError):
        return ToolResult(
            success=False,
            error="rate_limit",
            message="Too many requests. Please wait and try again.",
        )
    elif isinstance(e, ServerError):
        return ToolResult(
            success=False,
            error="server_error",
            message="Backend service temporarily unavailable. Please try again.",
        )
    elif isinstance(e, NetworkError):
        return ToolResult(
            success=False,
            error="network_error",
            message=str(e),
        )
    else:
        logger.error(f"Unexpected error in {operation}: {e}")
        return ToolResult(
            success=False,
            error="unexpected_error",
            message=f"Failed to {operation}: {str(e)}",
        )


# =============================================================================
# Ideation Tools
# =============================================================================


async def check_causality(
    args: Dict[str, Any], token_provider: TokenProvider
) -> ToolResult:
    """Check if a research question is causal."""
    model_map = {"sonnet": "databricks-claude-sonnet-4", "gpt4": "azure-openai-gpt4"}
    llm_model = model_map.get(
        args.get("llm_model", "sonnet"), "databricks-claude-sonnet-4"
    )

    try:
        response = await _api_request(
            "POST",
            "/api/v2/copilot/causality",
            token_provider,
            {"why_prompt": args["why_prompt"], "llm_model": llm_model},
        )
        is_causal = response.get("is_causal", False)
        return ToolResult(
            success=True,
            data=response,
            message=f"Question is {'causal' if is_causal else 'NOT causal - see suggestions'}",
        )
    except Exception as e:
        return _handle_error(e, "check causality")


async def generate_attributes_levels(
    args: Dict[str, Any], token_provider: TokenProvider
) -> ToolResult:
    """Generate attributes and levels for a conjoint experiment."""
    model_map = {"sonnet": "databricks-claude-sonnet-4", "gpt4": "azure-openai-gpt4"}
    llm_model = model_map.get(
        args.get("llm_model", "sonnet"), "databricks-claude-sonnet-4"
    )

    try:
        response = await _api_request(
            "POST",
            "/api/v1/attributes-levels-claude",
            token_provider,
            {
                "why_prompt": args["why_prompt"],
                "country": args.get("country", "United States"),
                "year": args.get("year", "2024"),
                "attribute_count": args.get("attribute_count", 5),
                "level_count": args.get("level_count", 4),
                "llm_model": llm_model,
            },
        )
        attrs = (
            response
            if isinstance(response, list)
            else response.get("attributes_levels", [])
        )
        return ToolResult(
            success=True,
            data={"attributes_levels": attrs},
            message=f"Generated {len(attrs)} attributes with levels",
        )
    except Exception as e:
        return _handle_error(e, "generate attributes and levels")


# =============================================================================
# Population Tools
# =============================================================================


async def validate_population(
    args: Dict[str, Any], token_provider: TokenProvider
) -> ToolResult:
    """Validate target population demographics."""
    try:
        response = await _api_request(
            "POST",
            "/api/v1/population/validate",
            token_provider,
            {
                "country": args.get("country", "United States of America (USA)"),
                "target_population": args.get("target_population", {}),
            },
        )
        return ToolResult(
            success=True,
            data=response,
            message="Population validated successfully",
        )
    except Exception as e:
        return _handle_error(e, "validate population")


async def get_population_stats(
    args: Dict[str, Any], token_provider: TokenProvider
) -> ToolResult:
    """Get population statistics for a country."""
    try:
        country = args.get("country", "United States of America (USA)")
        response = await _api_request(
            "GET",
            f"/api/v1/population/stats?{urlencode({'country': country})}",
            token_provider,
        )
        return ToolResult(
            success=True,
            data=response,
            message=f"Retrieved population stats for {country}",
        )
    except Exception as e:
        return _handle_error(e, "get population stats")


# =============================================================================
# Experiment Tools
# =============================================================================


async def create_experiment(
    args: Dict[str, Any], token_provider: TokenProvider
) -> ToolResult:
    """Create and run a conjoint experiment."""
    model_map = {"sonnet": "databricks-claude-sonnet-4", "gpt4": "azure-openai-gpt4"}
    llm_model = model_map.get(
        args.get("expr_llm_model", "sonnet"), "databricks-claude-sonnet-4"
    )

    country = args.get("country", "United States")
    if country == "United States":
        country = "United States of America (USA)"

    payload = {
        "why_prompt": args["why_prompt"],
        "country": country,
        "attribute_count": args.get("attribute_count", 5),
        "level_count": args.get("level_count", 4),
        "is_private": args.get("is_private", False),
        "expr_llm_model": llm_model,
        "experiment_type": "conjoint",
        "confidence_level": args.get("confidence_level", "Low"),
        "year": str(datetime.now().year),
        "target_population": {
            "age": [18, 75],
            "gender": ["Male", "Female"],
            "racial_group": [
                "White",
                "African American",
                "Asian or Pacific Islander",
                "Mixed race",
                "Other race",
            ],
            "education_level": [
                "High School Diploma",
                "Some College",
                "Bachelors",
                "Masters",
                "PhD",
            ],
            "household_income": [0, 300000],
            "number_of_children": ["0", "1", "2", "3", "4+"],
        },
        "latent_variables": True,
        "add_neither_option": True,
        "binary_choice": False,
        "match_population_distribution": False,
    }

    # Handle pre-cooked attributes
    if args.get("pre_cooked_attributes_and_levels_lookup"):
        raw_attrs = args["pre_cooked_attributes_and_levels_lookup"]
        formatted = []
        for item in raw_attrs:
            if isinstance(item, dict):
                formatted.append([item["attribute"], item["levels"]])
            elif isinstance(item, list) and len(item) >= 2:
                formatted.append(
                    item if isinstance(item[1], list) else [item[0], item[1:]]
                )
        payload["pre_cooked_attributes_and_levels_lookup"] = formatted

    try:
        response = await _api_request(
            "POST",
            "/api/v1/experiments",
            token_provider,
            payload,
        )
        run_id = response.get("run_id", response.get("id", "unknown"))
        return ToolResult(
            success=True,
            data=response,
            message=f"Experiment created with run_id: {run_id}",
        )
    except Exception as e:
        return _handle_error(e, "create experiment")


async def get_experiment_status(
    args: Dict[str, Any], token_provider: TokenProvider
) -> ToolResult:
    """Check experiment status."""
    try:
        response = await _api_request(
            "GET",
            f"/api/v1/runs/{args['run_id']}",
            token_provider,
        )
        status = response.get("status", "unknown")
        return ToolResult(
            success=True,
            data=response,
            message=f"Experiment status: {status}",
        )
    except Exception as e:
        return _handle_error(e, "get experiment status")


async def get_experiment_results(
    args: Dict[str, Any], token_provider: TokenProvider
) -> ToolResult:
    """Get experiment results."""
    try:
        response = await _api_request(
            "GET",
            f"/api/v1/runs/{args['run_id']}",
            token_provider,
        )
        return ToolResult(
            success=True,
            data=response,
            message="Retrieved experiment results",
        )
    except Exception as e:
        return _handle_error(e, "get experiment results")


async def list_experiments(
    args: Dict[str, Any], token_provider: TokenProvider
) -> ToolResult:
    """List all experiments."""
    try:
        response = await _api_request(
            "GET",
            "/api/v1/runs/all",
            token_provider,
        )
        runs = (
            response if isinstance(response, list) else response.get("runs", [])
        )
        limit = args.get("limit", 20)
        runs = runs[:limit]
        return ToolResult(
            success=True,
            data={"runs": runs, "count": len(runs)},
            message=f"Found {len(runs)} experiments",
        )
    except Exception as e:
        return _handle_error(e, "list experiments")


# =============================================================================
# Run Tools
# =============================================================================


async def get_run_details(
    args: Dict[str, Any], token_provider: TokenProvider
) -> ToolResult:
    """Get detailed run information."""
    try:
        response = await _api_request(
            "GET",
            f"/api/v1/runs/{args['run_id']}",
            token_provider,
        )
        return ToolResult(
            success=True,
            data=response,
            message="Retrieved run details",
        )
    except Exception as e:
        return _handle_error(e, "get run details")


async def get_run_artifacts(
    args: Dict[str, Any], token_provider: TokenProvider
) -> ToolResult:
    """Get run artifacts and files."""
    try:
        response = await _api_request(
            "GET",
            f"/api/v3/runs/{args['run_id']}/artifacts",
            token_provider,
        )
        return ToolResult(
            success=True,
            data=response,
            message="Retrieved run artifacts",
        )
    except Exception as e:
        return _handle_error(e, "get run artifacts")


async def update_run_config(
    args: Dict[str, Any], token_provider: TokenProvider
) -> ToolResult:
    """Update run configuration."""
    try:
        response = await _api_request(
            "POST",
            f"/api/v1/runs/{args['run_id']}/config",
            token_provider,
            args.get("config", {}),
        )
        return ToolResult(
            success=True,
            data=response,
            message="Run configuration updated",
        )
    except Exception as e:
        return _handle_error(e, "update run config")


# =============================================================================
# Persona Tools
# =============================================================================


async def generate_personas(
    args: Dict[str, Any], token_provider: TokenProvider
) -> ToolResult:
    """Generate AI personas for experiment."""
    try:
        count = args.get("count", 5)
        response = await _api_request(
            "POST",
            f"/api/v3/runs/{args['run_id']}/generate/personas",
            token_provider,
            {"count": count},
        )
        # Use actual count from response if available
        actual_count = len(response) if isinstance(response, list) else count
        return ToolResult(
            success=True,
            data=response,
            message=f"Generated {actual_count} personas",
        )
    except Exception as e:
        return _handle_error(e, "generate personas")


async def get_experiment_personas(
    args: Dict[str, Any], token_provider: TokenProvider
) -> ToolResult:
    """Get experiment personas."""
    try:
        response = await _api_request(
            "GET",
            f"/api/v3/runs/{args['run_id']}/personas",
            token_provider,
        )
        return ToolResult(
            success=True,
            data=response,
            message="Retrieved experiment personas",
        )
    except Exception as e:
        return _handle_error(e, "get experiment personas")


# =============================================================================
# Analytics Tools
# =============================================================================


async def get_amce_data(
    args: Dict[str, Any], token_provider: TokenProvider
) -> ToolResult:
    """Get AMCE (Average Marginal Component Effect) analytics data."""
    try:
        response = await _api_request(
            "GET",
            f"/api/v3/runs/{args['run_id']}/processed/amce",
            token_provider,
        )
        return ToolResult(
            success=True,
            data=response,
            message="Retrieved AMCE analytics data",
        )
    except Exception as e:
        return _handle_error(e, "get AMCE data")


async def get_causal_insights(
    args: Dict[str, Any], token_provider: TokenProvider
) -> ToolResult:
    """Get AI-generated causal insights."""
    try:
        response = await _api_request(
            "POST",
            f"/api/v3/runs/{args['run_id']}/generate/causal-sentences",
            token_provider,
            {},
        )
        sentences: list[str] = (
            [
                item.get("sentence", str(item)) if isinstance(item, dict) else str(item)
                for item in response
            ]
            if isinstance(response, list)
            else []
        )
        return ToolResult(
            success=True,
            data={"causal_statements": sentences},
            message=f"Generated {len(sentences)} causal insights",
        )
    except Exception as e:
        return _handle_error(e, "get causal insights")
