
from backend.app.agents.state.enums import (
    CustomerPatience,
    EscalationStatus,
    VerificationStatus,
)
from backend.app.agents.state.events import ConversationEvent
from backend.app.agents.state.models import ConversationState
from backend.app.scenarios.models import RulesConfig


def evaluate_escalation(
    state: ConversationState,
    rules: RulesConfig,
) -> ConversationEvent | None:
    """Return an escalation event when a configured rule matches."""

    if state.escalation in {
        EscalationStatus.REQUESTED,
        EscalationStatus.ESCALATED,
    }:
        return None

    if (
        rules.escalate_if_repeated_failures is not None
        and state.failure_count >= rules.escalate_if_repeated_failures
    ):
        return ConversationEvent.ESCALATION_TRIGGERED

    if (
        rules.escalate_if_patience_low
        and state.customer_patience == CustomerPatience.LOW
    ):
        return ConversationEvent.ESCALATION_TRIGGERED

    if (
        rules.escalate_if_identity_verification_fails
        and state.identity_verification == VerificationStatus.FAILED
    ):
        return ConversationEvent.ESCALATION_TRIGGERED

    return None



def test_escalation_does_not_trigger_when_already_requested():
    state = ConversationState(
        failure_count=3,
        escalation=EscalationStatus.REQUESTED,
    )
    rules = RulesConfig(escalate_if_repeated_failures=3)

    assert evaluate_escalation(state, rules) is None
