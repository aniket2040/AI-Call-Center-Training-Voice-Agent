from enum import StrEnum


class LifecycleEvent(StrEnum):
    APPLICATION_STARTUP = "application_startup"
    APPLICATION_SHUTDOWN = "application_shutdown"

    API_REQUEST = "api_request"

    TRAINING_SESSION_CREATED = "training_session_created"
    AGENT_DISPATCHED = "agent_dispatched"

    SIP_CALL_REQUESTED = "sip_call_requested"
    PARTICIPANT_CONNECTED = "participant_connected"

    CONVERSATION_STARTED = "conversation_started"
    CONVERSATION_ENDED = "conversation_ended"

    RECORDING_FINALIZED = "recording_finalized"
    TRANSCRIPT_FINALIZED = "transcript_finalized"

    EVALUATION_STARTED = "evaluation_started"
    EVALUATION_COMPLETED = "evaluation_completed"
    EVALUATION_FAILED = "evaluation_failed"