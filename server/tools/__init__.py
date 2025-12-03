"""MCP tools for Subconscious AI API."""

from .analytics import (
    get_amce_data_tool,
    get_causal_insights_tool,
    handle_get_amce_data,
    handle_get_causal_insights,
)
from .experiments import (
    create_experiment_tool,
    get_experiment_results_tool,
    get_experiment_status_tool,
    handle_create_experiment,
    handle_get_experiment_results,
    handle_get_experiment_status,
    handle_list_experiments,
    list_experiments_tool,
)
from .ideation import (
    check_causality_tool,
    check_moderation_tool,
    generate_attributes_levels_tool,
    handle_check_causality,
    handle_check_moderation,
    handle_generate_attributes_levels,
)
from .personas import (
    generate_personas_tool,
    get_experiment_personas_tool,
    handle_generate_personas,
    handle_get_experiment_personas,
)
from .population import (
    get_population_stats_tool,
    handle_get_population_stats,
    handle_validate_population,
    validate_population_tool,
)
from .runs import (
    get_run_artifacts_tool,
    get_run_details_tool,
    handle_get_run_artifacts,
    handle_get_run_details,
    handle_update_run_config,
    update_run_config_tool,
)

__all__ = [
    # Ideation (Step 1-3)
    "check_causality_tool",
    "handle_check_causality",
    "check_moderation_tool",
    "handle_check_moderation",
    "generate_attributes_levels_tool",
    "handle_generate_attributes_levels",
    # Population
    "validate_population_tool",
    "handle_validate_population",
    "get_population_stats_tool",
    "handle_get_population_stats",
    # Experiments
    "create_experiment_tool",
    "handle_create_experiment",
    "get_experiment_status_tool",
    "handle_get_experiment_status",
    "get_experiment_results_tool",
    "handle_get_experiment_results",
    "list_experiments_tool",
    "handle_list_experiments",
    # Runs
    "get_run_details_tool",
    "handle_get_run_details",
    "get_run_artifacts_tool",
    "handle_get_run_artifacts",
    "update_run_config_tool",
    "handle_update_run_config",
    # Personas
    "generate_personas_tool",
    "handle_generate_personas",
    "get_experiment_personas_tool",
    "handle_get_experiment_personas",
    # Analytics
    "get_amce_data_tool",
    "handle_get_amce_data",
    "get_causal_insights_tool",
    "handle_get_causal_insights",
]
