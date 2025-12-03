"""MCP tools for Subconscious AI API."""

from .experiments import (
    create_experiment_tool,
    handle_create_experiment,
    get_experiment_status_tool,
    handle_get_experiment_status,
    get_experiment_results_tool,
    handle_get_experiment_results,
    list_experiments_tool,
    handle_list_experiments,
)

from .runs import (
    get_run_details_tool,
    handle_get_run_details,
    get_run_artifacts_tool,
    handle_get_run_artifacts,
    update_run_config_tool,
    handle_update_run_config,
)

from .personas import (
    generate_personas_tool,
    handle_generate_personas,
    get_experiment_personas_tool,
    handle_get_experiment_personas,
)

from .population import (
    validate_population_tool,
    handle_validate_population,
    get_population_stats_tool,
    handle_get_population_stats,
)

from .analytics import (
    get_amce_data_tool,
    handle_get_amce_data,
    get_causal_insights_tool,
    handle_get_causal_insights,
)

from .ideation import (
    check_causality_tool,
    handle_check_causality,
    check_moderation_tool,
    handle_check_moderation,
    generate_attributes_levels_tool,
    handle_generate_attributes_levels,
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
