"""Pytest fixtures for MCP server tests."""

import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def mock_token_provider():
    """Mock token provider for testing."""
    from server.tools._core.base import TokenProvider

    provider = MagicMock(spec=TokenProvider)
    provider.get_token.return_value = "test_token_123"
    return provider


@pytest.fixture
def mock_api_response():
    """Factory for mock API responses."""

    def _factory(status_code: int = 200, json_data: dict = None):
        response = AsyncMock()
        response.status_code = status_code
        response.json.return_value = json_data or {}
        response.text = ""
        return response

    return _factory


@pytest.fixture
def sample_experiment_response():
    """Sample experiment creation response."""
    return {
        "run_id": "test-run-123",
        "wandb_run_id": "test-run-123",
        "wandb_run_name": "test-experiment",
        "status": "pending",
    }


@pytest.fixture
def sample_run_response():
    """Sample run details response."""
    return {
        "run_id": "test-run-123",
        "status": "completed",
        "state": "completed",
        "run_details": {
            "configs": {
                "experiment_design": {
                    "r_squared": 0.85,
                    "confidence_level": "High",
                }
            }
        },
    }


@pytest.fixture
def sample_attributes_response():
    """Sample attributes and levels response."""
    return [
        {"attribute": "Price", "levels": ["$10", "$20", "$30"]},
        {"attribute": "Brand", "levels": ["Brand A", "Brand B", "Brand C"]},
    ]
