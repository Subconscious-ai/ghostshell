"""Tests for tool handlers."""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock


class TestCheckCausality:
    """Tests for check_causality handler."""

    @pytest.mark.asyncio
    async def test_causal_question_returns_success(self, mock_token_provider):
        """Test that causal questions return success."""
        from server.tools._core.handlers import check_causality

        with patch("server.tools._core.handlers._api_request") as mock_request:
            mock_request.return_value = {"is_causal": True, "suggestions": []}

            result = await check_causality(
                {"why_prompt": "What factors influence EV adoption?"},
                mock_token_provider,
            )

            assert result.success is True
            assert result.data["is_causal"] is True
            assert "causal" in result.message.lower()

    @pytest.mark.asyncio
    async def test_non_causal_question_returns_suggestions(self, mock_token_provider):
        """Test that non-causal questions return suggestions."""
        from server.tools._core.handlers import check_causality

        with patch("server.tools._core.handlers._api_request") as mock_request:
            mock_request.return_value = {
                "is_causal": False,
                "suggestions": ["Rephrase to ask 'What factors influence...'"],
            }

            result = await check_causality(
                {"why_prompt": "Tell me about EVs"}, mock_token_provider
            )

            assert result.success is True
            assert result.data["is_causal"] is False
            assert "NOT causal" in result.message

    @pytest.mark.asyncio
    async def test_authentication_error_handled(self, mock_token_provider):
        """Test that authentication errors are handled properly."""
        from server.tools._core.handlers import check_causality
        from server.tools._core.exceptions import AuthenticationError

        with patch("server.tools._core.handlers._api_request") as mock_request:
            mock_request.side_effect = AuthenticationError("Token expired")

            result = await check_causality(
                {"why_prompt": "Test question"}, mock_token_provider
            )

            assert result.success is False
            assert result.error == "auth_error"
            assert "token" in result.message.lower()


class TestGenerateAttributesLevels:
    """Tests for generate_attributes_levels handler."""

    @pytest.mark.asyncio
    async def test_generates_attributes_successfully(
        self, mock_token_provider, sample_attributes_response
    ):
        """Test successful attribute generation."""
        from server.tools._core.handlers import generate_attributes_levels

        with patch("server.tools._core.handlers._api_request") as mock_request:
            mock_request.return_value = sample_attributes_response

            result = await generate_attributes_levels(
                {"why_prompt": "What factors influence EV adoption?"},
                mock_token_provider,
            )

            assert result.success is True
            assert "attributes_levels" in result.data
            assert len(result.data["attributes_levels"]) == 2


class TestCreateExperiment:
    """Tests for create_experiment handler."""

    @pytest.mark.asyncio
    async def test_creates_experiment_successfully(
        self, mock_token_provider, sample_experiment_response
    ):
        """Test successful experiment creation."""
        from server.tools._core.handlers import create_experiment

        with patch("server.tools._core.handlers._api_request") as mock_request:
            mock_request.return_value = sample_experiment_response

            result = await create_experiment(
                {"why_prompt": "What factors influence EV adoption?"},
                mock_token_provider,
            )

            assert result.success is True
            assert "run_id" in result.message.lower()

    @pytest.mark.asyncio
    async def test_handles_pre_cooked_attributes(self, mock_token_provider):
        """Test handling of pre-cooked attributes."""
        from server.tools._core.handlers import create_experiment

        with patch("server.tools._core.handlers._api_request") as mock_request:
            mock_request.return_value = {"run_id": "test-123"}

            pre_cooked = [
                {"attribute": "Price", "levels": ["$10", "$20"]},
                {"attribute": "Brand", "levels": ["A", "B"]},
            ]

            result = await create_experiment(
                {
                    "why_prompt": "Test question",
                    "pre_cooked_attributes_and_levels_lookup": pre_cooked,
                },
                mock_token_provider,
            )

            assert result.success is True
            # Verify the API was called with formatted attributes
            call_args = mock_request.call_args
            payload = call_args[0][3]  # Fourth argument is json_data
            assert "pre_cooked_attributes_and_levels_lookup" in payload


class TestListExperiments:
    """Tests for list_experiments handler."""

    @pytest.mark.asyncio
    async def test_lists_experiments_successfully(self, mock_token_provider):
        """Test successful experiment listing."""
        from server.tools._core.handlers import list_experiments

        with patch("server.tools._core.handlers._api_request") as mock_request:
            mock_request.return_value = [
                {"run_id": "run-1", "status": "completed"},
                {"run_id": "run-2", "status": "running"},
            ]

            result = await list_experiments({"limit": 10}, mock_token_provider)

            assert result.success is True
            assert result.data["count"] == 2
            assert len(result.data["runs"]) == 2

    @pytest.mark.asyncio
    async def test_respects_limit_parameter(self, mock_token_provider):
        """Test that limit parameter is respected."""
        from server.tools._core.handlers import list_experiments

        with patch("server.tools._core.handlers._api_request") as mock_request:
            mock_request.return_value = [
                {"run_id": f"run-{i}"} for i in range(10)
            ]

            result = await list_experiments({"limit": 3}, mock_token_provider)

            assert result.success is True
            assert result.data["count"] == 3


class TestGetExperimentStatus:
    """Tests for get_experiment_status handler."""

    @pytest.mark.asyncio
    async def test_gets_status_successfully(
        self, mock_token_provider, sample_run_response
    ):
        """Test successful status retrieval."""
        from server.tools._core.handlers import get_experiment_status

        with patch("server.tools._core.handlers._api_request") as mock_request:
            mock_request.return_value = sample_run_response

            result = await get_experiment_status(
                {"run_id": "test-run-123"}, mock_token_provider
            )

            assert result.success is True
            assert "completed" in result.message.lower()


class TestGetCausalInsights:
    """Tests for get_causal_insights handler."""

    @pytest.mark.asyncio
    async def test_gets_insights_successfully(self, mock_token_provider):
        """Test successful insights retrieval."""
        from server.tools._core.handlers import get_causal_insights

        with patch("server.tools._core.handlers._api_request") as mock_request:
            mock_request.return_value = [
                {"sentence": "Price has a significant positive effect."},
                {"sentence": "Brand awareness increases preference."},
            ]

            result = await get_causal_insights(
                {"run_id": "test-run-123"}, mock_token_provider
            )

            assert result.success is True
            assert "causal_statements" in result.data
            assert len(result.data["causal_statements"]) == 2
