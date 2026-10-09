from enum import StrEnum


class ConversationEvent(StrEnum):
    TURN_COMPLETED = "turn_completed"

    IDENTITY_VERIFICATION_STARTED = "identity_verification_started"
    IDENTITY_VERIFIED = "identity_verified"
    IDENTITY_VERIFICATION_FAILED = "identity_verification_failed"

    PROBLEM_DISCUSSED = "problem_discussed"
    PROBLEM_UNDERSTOOD = "problem_understood"

    EMPATHY_DETECTED = "empathy_detected"
    PROBLEM_IGNORED = "problem_ignored"

    RESOLUTION_STARTED = "resolution_started"
    RESOLUTION_OFFERED = "resolution_offered"
    RESOLUTION_ACCEPTED = "resolution_accepted"
    RESOLUTION_REJECTED = "resolution_rejected"

    ESCALATION_REQUESTED = "escalation_requested"
    ESCALATION_COMPLETED = "escalation_completed"

    REPEATED_QUESTION = "repeated_question"
    REPEATED_FAILURE = "repeated_failure"
    RESOLUTION_SUCCESSFUL = "resolution_successful"
    ESCALATION_TRIGGERED = "escalation_triggered"