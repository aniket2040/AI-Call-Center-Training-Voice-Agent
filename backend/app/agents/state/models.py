from pydantic import BaseModel, ConfigDict, Field

from backend.app.agents.state.enums import (
    CustomerMood,
    CustomerPatience,
    EmpathyStatus,
    EscalationStatus,
    ProblemUnderstandingStatus,
    ResolutionStatus,
    VerificationStatus,
)


class ConversationState(BaseModel):
    """
    Serializable and inspectable state of one training conversation.
    """

    model_config = ConfigDict(extra="forbid")

    customer_mood: CustomerMood = CustomerMood.NEUTRAL
    customer_patience: CustomerPatience = CustomerPatience.MEDIUM

    identity_verification: VerificationStatus = (
        VerificationStatus.NOT_STARTED
    )

    problem_understanding: ProblemUnderstandingStatus = (
        ProblemUnderstandingStatus.NOT_STARTED
    )

    empathy: EmpathyStatus = EmpathyStatus.NOT_DETECTED

    resolution: ResolutionStatus = (
        ResolutionStatus.NOT_STARTED
    )

    escalation: EscalationStatus = (
        EscalationStatus.NOT_REQUIRED
    )

    completed_objectives: set[str] = Field(
        default_factory=set,
    )

    turn_count: int = Field(
        default=0,
        ge=0,
    )

    def to_dict(self) -> dict:
        """Return a JSON-serializable representation."""
        return self.model_dump(mode="json")