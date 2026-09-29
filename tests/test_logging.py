import structlog
from backend.app.core.events import LifecycleEvent
from backend.app.core.logging import log_lifecycle_event
from backend.app.core.logging import (
    bind_request_context,
    get_logger,
)


def test_logger_is_available():
    logger = get_logger("test")

    assert logger is not None


def test_context_binding():
    bind_request_context(
        request_id="request-123",
        session_id="session-456",
        call_id="call-789",
    )

    context = structlog.contextvars.get_contextvars()

    assert context["request_id"] == "request-123"
    assert context["session_id"] == "session-456"
    assert context["call_id"] == "call-789"

    structlog.contextvars.clear_contextvars()




def test_lifecycle_events_are_defined():
    expected_events = {
        "application_startup",
        "application_shutdown",
        "api_request",
        "training_session_created",
        "agent_dispatched",
        "sip_call_requested",
        "participant_connected",
        "conversation_started",
        "conversation_ended",
        "recording_finalized",
        "transcript_finalized",
        "evaluation_started",
        "evaluation_completed",
        "evaluation_failed",
    }

    actual_events = {
        event.value
        for event in LifecycleEvent
    }

    assert actual_events == expected_events