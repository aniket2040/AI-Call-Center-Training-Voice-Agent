
from enum import StrEnum


class ConversationEvent(StrEnum):
    """Events used by the deterministic conversation state engine."""

    TURN_COMPLETED = "turn_completed"
    TOOL_EXECUTION_SUCCEEDED = "tool_execution_succeeded"
    TOOL_EXECUTION_FAILED = "tool_execution_failed"

    IDENTITY_VERIFICATION_STARTED = "identity_verification_started"
    IDENTITY_VERIFIED = "identity_verified"
    IDENTITY_VERIFICATION_FAILED = "identity_verification_failed"

    PROBLEM_DISCUSSED = "problem_discussed"
    PROBLEM_UNDERSTOOD = "problem_understood"
    EMPATHY_DETECTED = "empathy_detected"
    PROBLEM_IGNORED = "problem_ignored"
    REPEATED_QUESTION = "repeated_question"
    REPEATED_FAILURE = "repeated_failure"

    RESOLUTION_STARTED = "resolution_started"
    RESOLUTION_OFFERED = "resolution_offered"
    RESOLUTION_ACCEPTED = "resolution_accepted"
    RESOLUTION_REJECTED = "resolution_rejected"
    RESOLUTION_SUCCESSFUL = "resolution_successful"

    ESCALATION_REQUESTED = "escalation_requested"
    ESCALATION_TRIGGERED = "escalation_triggered"
    ESCALATION_COMPLETED = "escalation_completed"


class SessionEventType(StrEnum):
    """Persistent events recorded during a training session."""

    SESSION_CREATED = "SESSION_CREATED"
    AGENT_DISPATCHED = "AGENT_DISPATCHED"
    CALL_INITIATED = "CALL_INITIATED"
    PARTICIPANT_JOINED = "PARTICIPANT_JOINED"
    CONVERSATION_STARTED = "CONVERSATION_STARTED"
    USER_SPEECH = "USER_SPEECH"
    AGENT_SPEECH = "AGENT_SPEECH"
    TOOL_CALLED = "TOOL_CALLED"
    TOOL_COMPLETED = "TOOL_COMPLETED"
    STATE_CHANGED = "STATE_CHANGED"
    INTERRUPTION = "INTERRUPTION"
    CALL_ENDED = "CALL_ENDED"
    RECORDING_COMPLETED = "RECORDING_COMPLETED"
    TRANSCRIPT_COMPLETED = "TRANSCRIPT_COMPLETED"
    EVALUATION_STARTED = "EVALUATION_STARTED"
    EVALUATION_COMPLETED = "EVALUATION_COMPLETED"
    SESSION_FAILED = "SESSION_FAILED"
