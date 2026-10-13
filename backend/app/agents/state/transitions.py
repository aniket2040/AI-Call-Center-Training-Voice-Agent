from dataclasses import dataclass

from backend.app.agents.state.enums import (
    CustomerMood,
    CustomerPatience,
    EmpathyStatus,
    EscalationStatus,
    ProblemUnderstandingStatus,
    ResolutionStatus,
    VerificationStatus,
)
from backend.app.agents.state.events import ConversationEvent
from backend.app.agents.state.models import ConversationState


class InvalidStateTransition(ValueError):
    """Raised when a conversation state transition is invalid."""


@dataclass(frozen=True)
class TransitionContext:
    """Context required to perform a state transition."""

    objective: str | None = None


def apply_transition(
    state: ConversationState,
    event: ConversationEvent,
    context: TransitionContext | None = None,
) -> ConversationState:
    """
    Apply one deterministic transition to the conversation state.

    The original state is never mutated.
    A new state object is returned.
    """

    new_state = state.model_copy(deep=True)
    new_state.event_history.append(event.value)

    if event == ConversationEvent.TURN_COMPLETED:
        new_state.turn_count += 1
        return new_state

    if event in {
        ConversationEvent.TOOL_EXECUTION_SUCCEEDED,
        ConversationEvent.TOOL_EXECUTION_FAILED,
    }:
        return new_state

    if event == ConversationEvent.IDENTITY_VERIFICATION_STARTED:
        if new_state.identity_verification not in {
            VerificationStatus.NOT_STARTED,
            VerificationStatus.IN_PROGRESS,
        }:
            raise InvalidStateTransition(
                "Identity verification cannot be started "
                "after verification has completed or failed."
            )

        new_state.identity_verification = (
            VerificationStatus.IN_PROGRESS
        )
        return new_state

    if event == ConversationEvent.IDENTITY_VERIFIED:
        if new_state.identity_verification not in {
            VerificationStatus.IN_PROGRESS,
            VerificationStatus.VERIFIED,
        }:
            raise InvalidStateTransition(
                "Identity can only be verified after "
                "verification has started."
            )

        new_state.identity_verification = (
            VerificationStatus.VERIFIED
        )
        return new_state

    if event == ConversationEvent.IDENTITY_VERIFICATION_FAILED:
        if new_state.identity_verification not in {
            VerificationStatus.IN_PROGRESS,
            VerificationStatus.FAILED,
        }:
            raise InvalidStateTransition(
                "Identity verification has not started."
            )

        new_state.identity_verification = (
            VerificationStatus.FAILED
        )
        return new_state

    if event == ConversationEvent.PROBLEM_DISCUSSED:
        if new_state.problem_understanding == (
            ProblemUnderstandingStatus.NOT_STARTED
        ):
            new_state.problem_understanding = (
                ProblemUnderstandingStatus.IN_PROGRESS
            )

        return new_state

    if event == ConversationEvent.PROBLEM_UNDERSTOOD:
        if new_state.problem_understanding not in {
            ProblemUnderstandingStatus.IN_PROGRESS,
            ProblemUnderstandingStatus.UNDERSTOOD,
        }:
            raise InvalidStateTransition(
                "Problem cannot be marked understood before "
                "the problem has been discussed."
            )

        new_state.problem_understanding = (
            ProblemUnderstandingStatus.UNDERSTOOD
        )

        return new_state

    if event == ConversationEvent.EMPATHY_DETECTED:
        new_state.empathy = EmpathyStatus.DETECTED

        if new_state.customer_mood == CustomerMood.ANGRY:
            new_state.customer_mood = CustomerMood.FRUSTRATED
        elif new_state.customer_mood == CustomerMood.FRUSTRATED:
            new_state.customer_mood = CustomerMood.NEUTRAL
        elif new_state.customer_mood == CustomerMood.NEUTRAL:
            new_state.customer_mood = CustomerMood.CALM

        # Empathy increases the customer's patience.
        if new_state.customer_patience == CustomerPatience.LOW:
            new_state.customer_patience = CustomerPatience.MEDIUM
        elif new_state.customer_patience == CustomerPatience.MEDIUM:
            new_state.customer_patience = CustomerPatience.HIGH

        return new_state

    if event == ConversationEvent.PROBLEM_IGNORED:
        if new_state.customer_mood == CustomerMood.CALM:
            new_state.customer_mood = CustomerMood.NEUTRAL

        elif new_state.customer_mood == CustomerMood.NEUTRAL:
            new_state.customer_mood = CustomerMood.FRUSTRATED

        elif new_state.customer_mood == CustomerMood.FRUSTRATED:
            new_state.customer_mood = CustomerMood.ANGRY

        if new_state.customer_patience == CustomerPatience.HIGH:
            new_state.customer_patience = CustomerPatience.MEDIUM

        elif new_state.customer_patience == CustomerPatience.MEDIUM:
            new_state.customer_patience = CustomerPatience.LOW

        return new_state

    if event == ConversationEvent.REPEATED_QUESTION:
        new_state.repeated_question_count += 1

        if new_state.customer_patience == CustomerPatience.HIGH:
            new_state.customer_patience = CustomerPatience.MEDIUM
        elif new_state.customer_patience == CustomerPatience.MEDIUM:
            new_state.customer_patience = CustomerPatience.LOW

        return new_state

    if event == ConversationEvent.REPEATED_FAILURE:
        new_state.failure_count += 1

        if new_state.customer_mood == CustomerMood.CALM:
            new_state.customer_mood = CustomerMood.NEUTRAL
        elif new_state.customer_mood == CustomerMood.NEUTRAL:
            new_state.customer_mood = CustomerMood.FRUSTRATED
        elif new_state.customer_mood == CustomerMood.FRUSTRATED:
            new_state.customer_mood = CustomerMood.ANGRY

        if new_state.customer_patience == CustomerPatience.HIGH:
            new_state.customer_patience = CustomerPatience.MEDIUM
        elif new_state.customer_patience == CustomerPatience.MEDIUM:
            new_state.customer_patience = CustomerPatience.LOW

        return new_state

    if event == ConversationEvent.RESOLUTION_STARTED:
        if new_state.problem_understanding != (
            ProblemUnderstandingStatus.UNDERSTOOD
        ):
            raise InvalidStateTransition(
                "Resolution cannot start before the problem "
                "is understood."
            )

        new_state.resolution = ResolutionStatus.IN_PROGRESS
        return new_state

    if event == ConversationEvent.RESOLUTION_OFFERED:
        if new_state.resolution != ResolutionStatus.IN_PROGRESS:
            raise InvalidStateTransition(
                "Resolution cannot be offered before "
                "resolution handling has started."
            )

        new_state.resolution = ResolutionStatus.OFFERED
        return new_state

    if event == ConversationEvent.RESOLUTION_ACCEPTED:
        if new_state.resolution != ResolutionStatus.OFFERED:
            raise InvalidStateTransition(
                "Resolution cannot be accepted before "
                "it has been offered."
            )

        new_state.resolution = ResolutionStatus.ACCEPTED
        return new_state

    if event == ConversationEvent.RESOLUTION_REJECTED:
        if new_state.resolution != ResolutionStatus.OFFERED:
            raise InvalidStateTransition(
                "Resolution cannot be rejected before "
                "it has been offered."
            )

        new_state.resolution = ResolutionStatus.REJECTED
        return new_state

    if event == ConversationEvent.RESOLUTION_SUCCESSFUL:
        if new_state.resolution not in {
            ResolutionStatus.OFFERED,
            ResolutionStatus.ACCEPTED,
        }:
            raise InvalidStateTransition(
                "Successful resolution requires an offered "
                "or accepted resolution."
            )

        new_state.resolution = ResolutionStatus.ACCEPTED
        new_state.customer_mood = CustomerMood.SATISFIED
        return new_state

    if event == ConversationEvent.ESCALATION_REQUESTED:
        if new_state.escalation == EscalationStatus.ESCALATED:
            return new_state

        new_state.escalation = EscalationStatus.REQUESTED
        return new_state

    if event == ConversationEvent.ESCALATION_TRIGGERED:
        if new_state.escalation == EscalationStatus.ESCALATED:
            return new_state

        new_state.escalation = EscalationStatus.REQUESTED
        return new_state

    if event == ConversationEvent.ESCALATION_COMPLETED:
        if new_state.escalation != EscalationStatus.REQUESTED:
            raise InvalidStateTransition(
                "Escalation cannot be completed before "
                "it has been requested."
            )

        new_state.escalation = EscalationStatus.ESCALATED
        return new_state

    raise InvalidStateTransition(
        f"Unsupported conversation event: {event}"
    )


def complete_objective(
    state: ConversationState,
    objective: str,
) -> ConversationState:
    """
    Mark an objective as completed.

    Objective completion is idempotent.
    """

    objective = objective.strip()

    if not objective:
        raise InvalidStateTransition(
            "Objective cannot be empty."
        )

    new_state = state.model_copy(deep=True)

    new_state.completed_objectives.add(objective)

    return new_state