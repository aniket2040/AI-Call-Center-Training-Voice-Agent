
import pytest

from backend.app.lifecycle.transitions import (
    InvalidLifecycleTransition,
    validate_transition,
)
from backend.app.models.enums import TrainingSessionStatus as Status
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.engine import Result

from backend.app.lifecycle.service import (
    SessionLifecycleService,
    SessionNotFoundError,
)
@pytest.fixture
def lifecycle_mocks():
    session = SimpleNamespace(
        id=1,
        status=Status.CONNECTING.value,
        started_at=None,
        ended_at=None,
        updated_at=None,
        failure_reason=None,
    )

    db = MagicMock()
    db.execute = AsyncMock()
    db.flush = AsyncMock()

    result = MagicMock()
    result.scalar_one_or_none.return_value = session
    db.execute.return_value = result

    events = MagicMock()
    events.create = AsyncMock()

    service = SessionLifecycleService(db)
    service.events = events

    return service, db, events, session


def test_valid_transition():
    assert validate_transition(
        Status.CREATED,
        Status.DISPATCHING,
    ) is True


def test_same_state_is_idempotent():
    assert validate_transition(
        Status.ACTIVE,
        Status.ACTIVE,
    ) is False

@pytest.mark.asyncio
async def test_transition_updates_session_and_records_event(lifecycle_mocks):
    service, db, events, session = lifecycle_mocks

    updated_session = await service.transition(
        session_id=1,
        target=Status.ACTIVE,
    )

    assert updated_session.status == Status.ACTIVE.value
    assert updated_session.started_at is not None
    assert updated_session.updated_at is not None

    events.create.assert_awaited_once()

    event_kwargs = events.create.await_args.kwargs

    assert event_kwargs["session_id"] == 1
    assert event_kwargs["event_type"] == "lifecycle_transition"
    assert event_kwargs["payload"]["from_status"] == Status.CONNECTING.value
    assert event_kwargs["payload"]["to_status"] == Status.ACTIVE.value

    db.flush.assert_awaited_once()


def test_invalid_transition_is_rejected():
    with pytest.raises(InvalidLifecycleTransition):
        validate_transition(
            Status.ACTIVE,
            Status.COMPLETED,
        )


def test_terminal_state_cannot_transition():
    with pytest.raises(InvalidLifecycleTransition):
        validate_transition(
            Status.COMPLETED,
            Status.ACTIVE,
        )


def test_timeout_transition():
    assert validate_transition(
        Status.CONNECTING,
        Status.TIMEOUT,
    ) is True

@pytest.mark.asyncio
async def test_repeated_transition_is_idempotent(lifecycle_mocks):
    service, db, events, session = lifecycle_mocks

    session.status = Status.ACTIVE.value

    updated_session = await service.transition(
        session_id=1,
        target=Status.ACTIVE,
    )

    assert updated_session.status == Status.ACTIVE.value

    events.create.assert_not_awaited()
    db.flush.assert_not_awaited()

@pytest.mark.asyncio
async def test_failure_transition_stores_reason(lifecycle_mocks):
    service, db, events, session = lifecycle_mocks

    reason = "Agent connection failed"

    updated_session = await service.transition(
        session_id=1,
        target=Status.FAILED,
        reason=reason,
    )

    assert updated_session.status == Status.FAILED.value
    assert updated_session.failure_reason == reason
    assert updated_session.ended_at is not None

    events.create.assert_awaited_once()

    event_payload = events.create.await_args.kwargs["payload"]

    assert event_payload["from_status"] == Status.CONNECTING.value
    assert event_payload["to_status"] == Status.FAILED.value
    assert event_payload["reason"] == reason

    db.flush.assert_awaited_once()



@pytest.mark.asyncio
async def test_cancellation_sets_terminal_state(lifecycle_mocks):
    service, db, events, session = lifecycle_mocks

    updated_session = await service.transition(
        session_id=1,
        target=Status.CANCELLED,
        reason="Cancelled by trainee",
    )

    assert updated_session.status == Status.CANCELLED.value
    assert updated_session.ended_at is not None

    events.create.assert_awaited_once()
    db.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_timeout_sets_terminal_state(lifecycle_mocks):
    service, db, events, session = lifecycle_mocks

    updated_session = await service.transition(
        session_id=1,
        target=Status.TIMEOUT,
        reason="Connection timed out",
    )

    assert updated_session.status == Status.TIMEOUT.value
    assert updated_session.failure_reason == "Connection timed out"
    assert updated_session.ended_at is not None

    events.create.assert_awaited_once()
    db.flush.assert_awaited_once()



@pytest.mark.asyncio
async def test_missing_session_raises_error(lifecycle_mocks):
    service, db, events, session = lifecycle_mocks

    result = db.execute.return_value
    result.scalar_one_or_none.return_value = None

    with pytest.raises(SessionNotFoundError):
        await service.transition(
            session_id=999,
            target=Status.ACTIVE,
        )

    events.create.assert_not_awaited()
    db.flush.assert_not_awaited()



@pytest.mark.asyncio
async def test_complete_lifecycle_sequence(lifecycle_mocks):
    service, db, events, session = lifecycle_mocks

    session.status = Status.CREATED.value

    lifecycle = [
        Status.DISPATCHING,
        Status.CONNECTING,
        Status.ACTIVE,
        Status.ENDING,
        Status.COMPLETED,
    ]

    for target in lifecycle:
        await service.transition(
            session_id=1,
            target=target,
        )

    assert session.status == Status.COMPLETED.value

    assert session.started_at is not None
    assert session.ended_at is not None
    assert session.updated_at is not None

    assert events.create.await_count == 5
    assert db.flush.await_count == 5

    recorded_events = [
        call.kwargs["payload"]
        for call in events.create.await_args_list
    ]

    expected_transitions = [
        (Status.CREATED.value, Status.DISPATCHING.value),
        (Status.DISPATCHING.value, Status.CONNECTING.value),
        (Status.CONNECTING.value, Status.ACTIVE.value),
        (Status.ACTIVE.value, Status.ENDING.value),
        (Status.ENDING.value, Status.COMPLETED.value),
    ]

    actual_transitions = [
        (
            event["from_status"],
            event["to_status"],
        )
        for event in recorded_events
    ]

    assert actual_transitions == expected_transitions