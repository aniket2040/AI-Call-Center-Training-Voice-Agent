from pydantic import ValidationError

from backend.app.models import Scenario
from backend.app.scenarios.models import (
    EvaluationConfig,
    PersonaConfig,
    RulesConfig,
    ScenarioDefinition,
    SituationConfig,
)


class ScenarioValidationError(ValueError):
    """Raised when a database scenario contains invalid configuration."""


def validate_scenario(scenario: Scenario) -> ScenarioDefinition:
    """
    Validate and convert a database Scenario into an internal
    ScenarioDefinition.
    """

    try:
        rules_config = dict(scenario.rules_config or {})
        situation_config = rules_config.pop("situation", {})

        return ScenarioDefinition(
            id=str(scenario.id),
            name=scenario.name,
            difficulty=scenario.difficulty,
            persona=PersonaConfig.model_validate(
                scenario.persona_config,
            ),
            situation=SituationConfig.model_validate(
                situation_config,
            ),
            objectives=scenario.objectives,
            rules=RulesConfig.model_validate(
                rules_config,
            ),
            evaluation=EvaluationConfig.model_validate(
                scenario.evaluation_config,
            ),
        )

    except ValidationError as exc:
        raise ScenarioValidationError(
            f"Invalid scenario configuration for scenario "
            f"{scenario.id}: {exc}"
        ) from exc