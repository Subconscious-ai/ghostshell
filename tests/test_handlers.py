"""Tests for tool handlers."""

from unittest.mock import patch

import pytest


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
        from server.tools._core.exceptions import AuthenticationError
        from server.tools._core.handlers import check_causality

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


class TestRemainingHandlers:
    """Additional coverage for handlers not exercised above."""

    @pytest.mark.asyncio
    async def test_validate_population_success(self, mock_token_provider):
        """Test successful population validation."""
        from server.tools._core.handlers import validate_population

        with patch("server.tools._core.handlers._api_request") as mock_request:
            mock_request.return_value = {"valid": True}

            result = await validate_population({}, mock_token_provider)

            assert result.success is True
            assert result.data["valid"] is True

    @pytest.mark.asyncio
    async def test_get_population_stats_success(self, mock_token_provider):
        """Test successful population stats retrieval."""
        from server.tools._core.handlers import get_population_stats

        with patch("server.tools._core.handlers._api_request") as mock_request:
            mock_request.return_value = {"country": "United States of America (USA)"}

            result = await get_population_stats({}, mock_token_provider)

            assert result.success is True
            assert "population stats" in result.message.lower()

    @pytest.mark.asyncio
    async def test_get_experiment_results_success(
        self, mock_token_provider, sample_run_response
    ):
        """Test successful experiment results retrieval."""
        from server.tools._core.handlers import get_experiment_results

        with patch("server.tools._core.handlers._api_request") as mock_request:
            mock_request.return_value = sample_run_response

            result = await get_experiment_results(
                {"run_id": "test-run-123"}, mock_token_provider
            )

            assert result.success is True
            assert result.data["run_id"] == "test-run-123"

    @pytest.mark.asyncio
    async def test_get_run_details_success(self, mock_token_provider):
        """Test successful run details retrieval."""
        from server.tools._core.handlers import get_run_details

        with patch("server.tools._core.handlers._api_request") as mock_request:
            mock_request.return_value = {"run_id": "run-1", "state": "completed"}

            result = await get_run_details({"run_id": "run-1"}, mock_token_provider)

            assert result.success is True
            assert result.data["run_id"] == "run-1"

    @pytest.mark.asyncio
    async def test_get_run_artifacts_success(self, mock_token_provider):
        """Test successful run artifacts retrieval."""
        from server.tools._core.handlers import get_run_artifacts

        with patch("server.tools._core.handlers._api_request") as mock_request:
            mock_request.return_value = {"artifacts": [{"name": "amce.csv"}]}

            result = await get_run_artifacts({"run_id": "run-1"}, mock_token_provider)

            assert result.success is True
            assert len(result.data["artifacts"]) == 1

    @pytest.mark.asyncio
    async def test_update_run_config_success(self, mock_token_provider):
        """Test successful run config update."""
        from server.tools._core.handlers import update_run_config

        with patch("server.tools._core.handlers._api_request") as mock_request:
            mock_request.return_value = {"updated": True}

            result = await update_run_config(
                {"run_id": "run-1", "config": {"test_mode": True}},
                mock_token_provider,
            )

            assert result.success is True
            assert result.data["updated"] is True
            call_args = mock_request.call_args
            payload = call_args[0][3]
            assert payload == {"config_update": {"test_mode": True}}

    @pytest.mark.asyncio
    async def test_generate_personas_success(self, mock_token_provider):
        """Test successful persona generation."""
        from server.tools._core.handlers import generate_personas

        with patch("server.tools._core.handlers._api_request") as mock_request:
            mock_request.return_value = [{"id": "p1"}, {"id": "p2"}]

            result = await generate_personas(
                {"run_id": "run-1", "count": 2}, mock_token_provider
            )

            assert result.success is True
            assert isinstance(result.data, list)
            assert "generated 2 personas" in result.message.lower()

    @pytest.mark.asyncio
    async def test_get_experiment_personas_success(self, mock_token_provider):
        """Test successful persona retrieval."""
        from server.tools._core.handlers import get_experiment_personas

        with patch("server.tools._core.handlers._api_request") as mock_request:
            mock_request.return_value = [{"id": "p1"}]

            result = await get_experiment_personas(
                {"run_id": "run-1"}, mock_token_provider
            )

            assert result.success is True
            assert len(result.data) == 1

    @pytest.mark.asyncio
    async def test_get_amce_data_success(self, mock_token_provider):
        """Test successful AMCE data retrieval."""
        from server.tools._core.handlers import get_amce_data

        with patch("server.tools._core.handlers._api_request") as mock_request:
            mock_request.return_value = {"amce": {"price": -0.2}}

            result = await get_amce_data({"run_id": "run-1"}, mock_token_provider)

            assert result.success is True
            assert "amce" in result.data


class TestErrorMappingCoverage:
    """Ensure every handler maps auth failures consistently."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("handler_name", "arguments"),
        [
            ("check_causality", {"why_prompt": "x"}),
            ("generate_attributes_levels", {"why_prompt": "x"}),
            ("validate_population", {}),
            ("get_population_stats", {}),
            ("create_experiment", {"why_prompt": "x"}),
            ("get_experiment_status", {"run_id": "run-1"}),
            ("get_experiment_results", {"run_id": "run-1"}),
            ("list_experiments", {}),
            ("get_run_details", {"run_id": "run-1"}),
            ("get_run_artifacts", {"run_id": "run-1"}),
            ("update_run_config", {"run_id": "run-1"}),
            ("generate_personas", {"run_id": "run-1"}),
            ("get_experiment_personas", {"run_id": "run-1"}),
            ("get_amce_data", {"run_id": "run-1"}),
            ("get_causal_insights", {"run_id": "run-1"}),
        ],
    )
    async def test_all_handlers_map_auth_errors(
        self, handler_name, arguments, mock_token_provider
    ):
        """Every handler should return standardized auth errors."""
        from server.tools._core import handlers
        from server.tools._core.exceptions import AuthenticationError

        handler = getattr(handlers, handler_name)
        with patch("server.tools._core.handlers._api_request") as mock_request:
            mock_request.side_effect = AuthenticationError("token expired")
            result = await handler(arguments, mock_token_provider)

        assert result.success is False
        assert result.error == "auth_error"
