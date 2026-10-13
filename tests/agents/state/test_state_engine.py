import json

import pytest

from backend.app.agents.state import (
    ConversationEvent,
    ConversationState,
    ConversationStateEngine,
    CustomerMood,
    CustomerPatience,
    EmpathyStatus,
    InvalidStateTransition,
    ProblemUnderstandingStatus,
    ResolutionStatus,
    VerificationStatus, EscalationStatus,
)


def test_initial_state():
    state = ConversationState()

    assert state.customer_mood == CustomerMood.NEUTRAL
    assert state.customer_patience == CustomerPatience.MEDIUM
    assert (
        state.identity_verification
        == VerificationStatus.NOT_STARTED
    )
    assert (
        state.problem_understanding
        == ProblemUnderstandingStatus.NOT_STARTED
    )
    assert state.empathy == EmpathyStatus.NOT_DETECTED
    assert state.resolution == ResolutionStatus.NOT_STARTED
    assert state.turn_count == 0
    assert state.completed_objectives == set()


def test_empathy_calms_frustrated_customer():
    engine = ConversationStateEngine(
        ConversationState(
            customer_mood=CustomerMood.FRUSTRATED,
        )
    )

    state = engine.apply_event(
        ConversationEvent.EMPATHY_DETECTED,
    )

    assert state.empathy == EmpathyStatus.DETECTED
    assert state.customer_mood == CustomerMood.NEUTRAL


def test_empathy_calms_angry_customer():
    engine = ConversationStateEngine(
        ConversationState(
            customer_mood=CustomerMood.ANGRY,
        )
    )

    state = engine.apply_event(
        ConversationEvent.EMPATHY_DETECTED,
    )

    assert state.customer_mood == CustomerMood.FRUSTRATED


def test_ignoring_problem_increases_frustration():
    engine = ConversationStateEngine(
        ConversationState(
            customer_mood=CustomerMood.NEUTRAL,
            customer_patience=CustomerPatience.MEDIUM,
        )
    )

    state = engine.apply_event(
        ConversationEvent.PROBLEM_IGNORED,
    )

    assert state.customer_mood == CustomerMood.FRUSTRATED
    assert state.customer_patience == CustomerPatience.LOW


def test_turn_count_increases():
    engine = ConversationStateEngine()

    engine.apply_event(
        ConversationEvent.TURN_COMPLETED,
    )

    engine.apply_event(
        ConversationEvent.TURN_COMPLETED,
    )

    assert engine.state.turn_count == 2


def test_identity_verification_transition():
    engine = ConversationStateEngine()

    engine.apply_event(
        ConversationEvent.IDENTITY_VERIFICATION_STARTED,
    )

    state = engine.apply_event(
        ConversationEvent.IDENTITY_VERIFIED,
    )

    assert (
        state.identity_verification
        == VerificationStatus.VERIFIED
    )


def test_cannot_verify_before_verification_starts():
    engine = ConversationStateEngine()

    with pytest.raises(InvalidStateTransition):
        engine.apply_event(
            ConversationEvent.IDENTITY_VERIFIED,
        )


def test_problem_must_be_understood_before_resolution():
    engine = ConversationStateEngine()

    with pytest.raises(InvalidStateTransition):
        engine.apply_event(
            ConversationEvent.RESOLUTION_STARTED,
        )


def test_resolution_flow():
    engine = ConversationStateEngine()

    engine.apply_event(
        ConversationEvent.PROBLEM_DISCUSSED,
    )

    engine.apply_event(
        ConversationEvent.PROBLEM_UNDERSTOOD,
    )

    engine.apply_event(
        ConversationEvent.RESOLUTION_STARTED,
    )

    state = engine.apply_event(
        ConversationEvent.RESOLUTION_OFFERED,
    )

    assert state.resolution == ResolutionStatus.OFFERED

    state = engine.apply_event(
        ConversationEvent.RESOLUTION_ACCEPTED,
    )

    assert state.resolution == ResolutionStatus.ACCEPTED


def test_objective_completion():
    engine = ConversationStateEngine(
        allowed_objectives=["show_empathy"],
    )

    state = engine.complete_objective("show_empathy")
    assert "show_empathy" in state.completed_objectives

    # Completion is idempotent.
    state = engine.complete_objective("show_empathy")
    assert len(state.completed_objectives) == 1


def test_unauthorized_objective_is_rejected():
    engine = ConversationStateEngine(
        allowed_objectives=["show_empathy"],
    )

    with pytest.raises(InvalidStateTransition):
        engine.complete_objective("issue_refund")

    assert "issue_refund" not in engine.state.completed_objectives


def test_empty_objective_is_rejected():
    engine = ConversationStateEngine(
        allowed_objectives=["show_empathy"],
    )

    with pytest.raises(InvalidStateTransition):
        engine.complete_objective("")

    assert not engine.state.completed_objectives


def test_state_is_serializable():
    engine = ConversationStateEngine()

    engine.apply_event(
        ConversationEvent.EMPATHY_DETECTED,
    )

    serialized = engine.serialize()

    assert isinstance(serialized, dict)
    assert serialized["customer_mood"] == "calm"

    # Prove it can be JSON encoded.
    encoded = json.dumps(serialized)

    assert isinstance(encoded, str)



def test_state_is_inspectable_without_mutating_it():
    engine = ConversationStateEngine()

    engine.apply_event(ConversationEvent.TURN_COMPLETED)
    state = engine.state

    state.turn_count = 999
    state.event_history.append("unauthorized_event")
    state.completed_objectives.add("unauthorized_objective")

    internal_state = engine.state

    assert internal_state.turn_count == 1
    assert "unauthorized_event" not in internal_state.event_history
    assert "unauthorized_objective" not in internal_state.completed_objectives



def test_transition_does_not_mutate_original_state():
    initial = ConversationState(
        customer_mood=CustomerMood.FRUSTRATED,
    )

    engine = ConversationStateEngine(initial)

    engine.apply_event(
        ConversationEvent.EMPATHY_DETECTED,
    )

    assert initial.customer_mood == CustomerMood.FRUSTRATED
    assert engine.state.customer_mood == CustomerMood.NEUTRAL



def test_empathy_increases_customer_patience():
    engine = ConversationStateEngine(
        ConversationState(
            customer_patience=CustomerPatience.LOW,
        )
    )

    state = engine.apply_event(
        ConversationEvent.EMPATHY_DETECTED,
    )

    assert state.customer_patience == CustomerPatience.MEDIUM

    state = engine.apply_event(
        ConversationEvent.EMPATHY_DETECTED,
    )

    assert state.customer_patience == CustomerPatience.HIGH


def test_repeated_question_reduces_patience():
    engine = ConversationStateEngine()

    state = engine.apply_event(
        ConversationEvent.REPEATED_QUESTION,
    )

    assert state.repeated_question_count == 1
    assert state.customer_patience == CustomerPatience.LOW

    state = engine.apply_event(
        ConversationEvent.REPEATED_QUESTION,
    )

    assert state.repeated_question_count == 2
    assert state.customer_patience == CustomerPatience.LOW


def test_repeated_failures_increase_frustration():
    engine = ConversationStateEngine(
        ConversationState(
            customer_mood=CustomerMood.CALM,
            customer_patience=CustomerPatience.HIGH,
        )
    )

    state = engine.apply_event(
        ConversationEvent.REPEATED_FAILURE,
    )

    assert state.failure_count == 1
    assert state.customer_mood == CustomerMood.NEUTRAL
    assert state.customer_patience == CustomerPatience.MEDIUM

    state = engine.apply_event(
        ConversationEvent.REPEATED_FAILURE,
    )

    assert state.failure_count == 2
    assert state.customer_mood == CustomerMood.FRUSTRATED
    assert state.customer_patience == CustomerPatience.LOW


def test_successful_resolution_makes_customer_satisfied():
    engine = ConversationStateEngine()

    engine.apply_event(ConversationEvent.PROBLEM_DISCUSSED)
    engine.apply_event(ConversationEvent.PROBLEM_UNDERSTOOD)
    engine.apply_event(ConversationEvent.RESOLUTION_STARTED)
    engine.apply_event(ConversationEvent.RESOLUTION_OFFERED)

    state = engine.apply_event(
        ConversationEvent.RESOLUTION_SUCCESSFUL,
    )

    assert state.resolution == ResolutionStatus.ACCEPTED
    assert state.customer_mood == CustomerMood.SATISFIED


def test_successful_resolution_requires_offer():
    engine = ConversationStateEngine()

    with pytest.raises(InvalidStateTransition):
        engine.apply_event(
            ConversationEvent.RESOLUTION_SUCCESSFUL,
        )


def test_escalation_triggered_requests_escalation():
    engine = ConversationStateEngine()

    state = engine.apply_event(
        ConversationEvent.ESCALATION_TRIGGERED,
    )

    assert state.escalation == EscalationStatus.REQUESTED


def test_escalation_can_be_completed_after_trigger():
    engine = ConversationStateEngine()

    engine.apply_event(
        ConversationEvent.ESCALATION_TRIGGERED,
    )

    state = engine.apply_event(
        ConversationEvent.ESCALATION_COMPLETED,
    )

    assert state.escalation == EscalationStatus.ESCALATED





def test_event_history_records_applied_events():
    engine = ConversationStateEngine()

    engine.apply_event(ConversationEvent.EMPATHY_DETECTED)
    engine.apply_event(ConversationEvent.PROBLEM_IGNORED)

    assert engine.state.event_history == [
        "empathy_detected",
        "problem_ignored",
    ]


def test_event_history_is_serializable():
    engine = ConversationStateEngine()

    engine.apply_event(
        ConversationEvent.ESCALATION_TRIGGERED,
    )

    assert engine.serialize()["event_history"] == [
        "escalation_triggered",
    ]



def test_successful_tool_execution_is_recorded_without_changing_business_state():
    engine = ConversationStateEngine()
    before = engine.state

    state = engine.record_tool_execution(succeeded=True)

    assert state.event_history == ["tool_execution_succeeded"]
    assert state.customer_mood == before.customer_mood
    assert state.customer_patience == before.customer_patience
    assert state.resolution == before.resolution
    assert state.escalation == before.escalation


def test_failed_tool_execution_is_recorded_without_changing_business_state():
    engine = ConversationStateEngine()
    before = engine.state

    state = engine.record_tool_execution(succeeded=False)

    assert state.event_history == ["tool_execution_failed"]
    assert state.customer_mood == before.customer_mood
    assert state.customer_patience == before.customer_patience
    assert state.resolution == before.resolution
    assert state.escalation == before.escalation

