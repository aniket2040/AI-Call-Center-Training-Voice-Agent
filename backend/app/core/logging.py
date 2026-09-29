import logging
import sys

import structlog

from backend.app.config import settings
from backend.app.core.events import LifecycleEvent


def configure_logging() -> None:
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level),
        force=True,
    )

    structlog.contextvars.clear_contextvars()

    structlog.contextvars.bind_contextvars(
        service=settings.app_name,
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(
                fmt="iso",
                utc=True,
            ),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.log_level),
        ),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

def get_logger(name: str = "application") -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name)


def bind_request_context(
    *,
    request_id: str | None = None,
    session_id: str | None = None,
    call_id: str | None = None,
) -> None:
    values = {}

    if request_id:
        values["request_id"] = request_id

    if session_id:
        values["session_id"] = session_id

    if call_id:
        values["call_id"] = call_id

    if values:
        structlog.contextvars.bind_contextvars(**values)


def log_lifecycle_event(
    event: LifecycleEvent,
    *,
    session_id: str | None = None,
    call_id: str | None = None,
    **metadata,
) -> None:
    logger = get_logger("lifecycle")

    logger.info(
        event.value,
        session_id=session_id,
        call_id=call_id,
        **metadata,
    )