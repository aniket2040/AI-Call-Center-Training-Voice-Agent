import structlog

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