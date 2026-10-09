
from backend.app.agents.state.enums import (
    CustomerMood,
    CustomerPatience,
    EscalationStatus,
)
from backend.app.agents.state.events import ConversationEvent
from backend.app.agents.training_customer import (
    TrainingCustomer,
    TrainingScenarioMetadata,
)


def make_scenario(**overrides) -> TrainingScenarioMetadata:
    data = {
        "scenario_id": 1,
        "name": "Refund complaint",
        "persona": "An unhappy customer",
        "situation": "A refund has not arrived",
        "rules": [],
        "objectives": [],
    }
    data.update(overrides)
    return TrainingScenarioMetadata(**data)


def make_customer(**overrides) -> TrainingCustomer:
    return TrainingCustomer(make_scenario(**overrides))


def test_empathy_reduces_frustration_and_improves_patience():
    customer = make_customer()

    customer.apply_behavior_event(ConversationEvent.PROBLEM_IGNORED)
    state = customer.apply_behavior_event(
        ConversationEvent.EMPATHY_DETECTED
    )

    assert state["customer_mood"] == CustomerMood.NEUTRAL
    assert state["customer_patience"] == CustomerPatience.MEDIUM


def test_repeated_failures_increase_frustration():
    customer = make_customer()

    state = customer.apply_behavior_event(
        ConversationEvent.REPEATED_FAILURE
    )

    assert state["failure_count"] == 1
    assert state["customer_mood"] == CustomerMood.FRUSTRATED


def test_failure_threshold_triggers_escalation():
    customer = make_customer(escalate_if_repeated_failures=2)

    customer.apply_behavior_event(ConversationEvent.REPEATED_FAILURE)
    state = customer.apply_behavior_event(
        ConversationEvent.REPEATED_FAILURE
    )

    assert state["failure_count"] == 2
    assert state["escalation"] == EscalationStatus.REQUESTED
    assert (
        state["event_history"][-1]
        == ConversationEvent.ESCALATION_TRIGGERED.value
    )


def test_each_customer_has_independent_state():
    first = make_customer()
    second = make_customer()

    first.apply_behavior_event(ConversationEvent.REPEATED_FAILURE)

    assert first.state_engine.state.failure_count == 1
    assert second.state_engine.state.failure_count == 0



def test_automatic_escalation_records_supervisor_escalation():
    customer = make_customer(escalate_if_repeated_failures=1)

    state = customer.apply_behavior_event(
        ConversationEvent.REPEATED_FAILURE
    )

    assert state["escalation"] == EscalationStatus.REQUESTED
    assert customer.tool_state.escalated is True
    assert customer.tool_state.escalation_id is not None
    assert (
        customer.tool_state.escalation_reason
        == "Repeated failure threshold reached"
    )
