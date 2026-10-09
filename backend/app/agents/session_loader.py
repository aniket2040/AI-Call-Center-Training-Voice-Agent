
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.agents.dispatch_metadata import DispatchMetadata
from backend.app.models.scenario import Scenario
from backend.app.models.training_session import TrainingSession
from backend.app.agents.training_customer import TrainingScenarioMetadata

class AgentSessionValidationError(ValueError):
    """Raised when an agent cannot load a valid training session."""


async def load_agent_session(
    db: AsyncSession,
    metadata: DispatchMetadata,
    *,
    room_name: str,
) -> tuple[TrainingSession, Scenario]:
    if not room_name:
        raise AgentSessionValidationError(
            "LiveKit room name is missing."
        )

    session = await db.get(TrainingSession, metadata.session_id)

    if session is None:
        raise AgentSessionValidationError(
            "Training session does not exist."
        )

    if session.trainee_id != metadata.trainee_id:
        raise AgentSessionValidationError(
            "Trainee ID does not match the training session."
        )

    if session.scenario_id != metadata.scenario_id:
        raise AgentSessionValidationError(
            "Scenario ID does not match the training session."
        )

    if session.livekit_room_name != room_name:
        raise AgentSessionValidationError(
            "LiveKit room does not match the training session."
        )

    scenario = await db.get(Scenario, metadata.scenario_id)

    if scenario is None:
        raise AgentSessionValidationError(
            "Scenario does not exist."
        )

    if not scenario.is_active:
        raise AgentSessionValidationError(
            "Scenario is inactive."
        )

    return session, scenario




def build_training_scenario(scenario: Scenario) -> TrainingScenarioMetadata:
    persona_config = scenario.persona_config or {}
    rules_config = scenario.rules_config or {}

    persona = persona_config.get("persona")
    situation = persona_config.get("situation")
    rules = rules_config.get("rules")

    escalate_if_repeated_failures = rules_config.get(
        "escalate_if_repeated_failures"
    )
    escalate_if_patience_low = rules_config.get(
        "escalate_if_patience_low", False
    )
    escalate_if_identity_verification_fails = rules_config.get(
        "escalate_if_identity_verification_fails", False
    )

    if not isinstance(persona, str) or not persona.strip():
        raise AgentSessionValidationError(
            "Scenario persona configuration is missing a valid persona."
        )

    if not isinstance(situation, str) or not situation.strip():
        raise AgentSessionValidationError(
            "Scenario persona configuration is missing a valid situation."
        )

    if not isinstance(rules, list) or not all(
        isinstance(rule, str) and rule.strip() for rule in rules
    ):
        raise AgentSessionValidationError(
            "Scenario rules configuration must contain a list of non-empty strings."
        )

    if not isinstance(scenario.objectives, list) or not all(
        isinstance(objective, str) and objective.strip()
        for objective in scenario.objectives
    ):
        raise AgentSessionValidationError(
            "Scenario objectives must be a list of non-empty strings."
        )

    return TrainingScenarioMetadata(
        scenario_id=scenario.id,
        name=scenario.name,
        persona=persona,
        situation=situation,
        rules=rules,
        objectives=scenario.objectives,
        escalate_if_repeated_failures=escalate_if_repeated_failures,
        escalate_if_patience_low=escalate_if_patience_low,
        escalate_if_identity_verification_fails=(
            escalate_if_identity_verification_fails
        ),
    )
