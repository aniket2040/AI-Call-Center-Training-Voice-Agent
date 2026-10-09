
import pytest

from backend.app.agents.state import (
    ConversationEvent,
    ConversationState,
    CustomerPatience,
    EscalationStatus,
    VerificationStatus,
    evaluate_escalation,
)
from backend.app.scenarios.models import RulesConfig


@pytest.mark.parametrize(
    ("state", "rules"),
    [
        (
            ConversationState(failure_count=3),
            RulesConfig(escalate_if_repeated_failures=3),
        ),
        (
            ConversationState(
                customer_patience=CustomerPatience.LOW,
            ),
            RulesConfig(escalate_if_patience_low=True),
        ),
        (
            ConversationState(
                identity_verification=VerificationStatus.FAILED,
            ),
            RulesConfig(
                escalate_if_identity_verification_fails=True,
            ),
        ),
    ],
)
def test_configured_escalation_rules_trigger(state, rules):
    assert evaluate_escalation(state, rules) == (
        ConversationEvent.ESCALATION_TRIGGERED
    )


def test_escalation_does_not_trigger_without_matching_rule():
    state = ConversationState(failure_count=1)
    rules = RulesConfig(escalate_if_repeated_failures=3)

    assert evaluate_escalation(state, rules) is None


def test_escalation_does_not_trigger_when_already_escalated():
    state = ConversationState(escalation=EscalationStatus.ESCALATED)
    rules = RulesConfig(escalate_if_patience_low=True)

    assert evaluate_escalation(state, rules) is None
