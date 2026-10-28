
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

import backend.app.agent_worker as worker
from backend.app.agents.state.events import SessionEventType


@pytest.mark.asyncio
async def test_runtime_exception_records_and_drains_session_failed(
    monkeypatch,
):
    training_session = SimpleNamespace(
        id=10,
        trainee_id=1,
        scenario_id=2,
    )
    db_scenario = SimpleNamespace(id=2, is_active=True)
    scenario = SimpleNamespace(scenario_id=2)

    db_context = MagicMock()
    db_context.__aenter__ = AsyncMock(return_value=MagicMock())
    db_context.__aexit__ = AsyncMock(return_value=False)

    event_recorder = MagicMock()
    event_recorder.drain = AsyncMock()

    session = MagicMock()
    session.start = AsyncMock(
        side_effect=RuntimeError("simulated session start failure")
    )

    ctx = SimpleNamespace(
        room=SimpleNamespace(
            name="test-room",
            remote_participants={},
            on=MagicMock(),
        ),
        job=SimpleNamespace(metadata="{}"),
        add_shutdown_callback=MagicMock(),
    )

    monkeypatch.setattr(
        worker,
        "parse_dispatch_metadata",
        MagicMock(return_value=SimpleNamespace(call_id="call-10")),
    )
    monkeypatch.setattr(
        worker,
        "AsyncSessionFactory",
        MagicMock(return_value=db_context),
    )
    monkeypatch.setattr(
        worker,
        "load_agent_session",
        AsyncMock(return_value=(training_session, db_scenario)),
    )
    monkeypatch.setattr(
        worker,
        "build_training_scenario",
        MagicMock(return_value=scenario),
    )
    monkeypatch.setattr(
        worker,
        "create_training_session",
        MagicMock(return_value=session),
    )
    monkeypatch.setattr(
        worker,
        "TrainingCustomer",
        MagicMock(return_value=MagicMock()),
    )
    monkeypatch.setattr(
        worker,
        "SessionEventRecorder",
        MagicMock(return_value=event_recorder),
    )
    monkeypatch.setattr(
        worker,
        "register_session_events",
        MagicMock(),
    )
    monkeypatch.setattr(
        worker,
        "register_transcript_events",
        MagicMock(),
    )
    monkeypatch.setattr(
        worker,
        "register_tool_execution_events",
        MagicMock(),
    )

    with pytest.raises(
        RuntimeError,
        match="simulated session start failure",
    ):
        await worker.training_agent(ctx)

    event_recorder.record.assert_any_call(
        SessionEventType.SESSION_FAILED,
        {
            "stage": "agent_runtime",
            "error_type": "RuntimeError",
            "reason": "simulated session start failure",
            "room_name": "test-room",
        },
    )
    event_recorder.drain.assert_awaited_once()



@pytest.mark.asyncio
async def test_participant_joined_is_recorded_only_once(monkeypatch):
    training_session = SimpleNamespace(
        id=10,
        trainee_id=1,
        scenario_id=2,
    )
    db_scenario = SimpleNamespace(id=2, is_active=True)
    scenario = SimpleNamespace(scenario_id=2)

    participant = SimpleNamespace(
        identity="trainee-1",
        sid="PA_test123",
    )

    db_context = MagicMock()
    db_context.__aenter__ = AsyncMock(return_value=MagicMock())
    db_context.__aexit__ = AsyncMock(return_value=False)

    event_recorder = MagicMock()
    event_recorder.drain = AsyncMock()

    session = MagicMock()
    session.start = AsyncMock()

    registered_callbacks = {}

    def register_room_event(event_name):
        def decorator(callback):
            registered_callbacks[event_name] = callback
            return callback

        return decorator

    room = SimpleNamespace(
        name="test-room",
        remote_participants={participant.sid: participant},
        on=register_room_event,
    )

    ctx = SimpleNamespace(
        room=room,
        job=SimpleNamespace(metadata="{}"),
        add_shutdown_callback=MagicMock(),
    )

    monkeypatch.setattr(
        worker,
        "parse_dispatch_metadata",
        MagicMock(return_value=SimpleNamespace(call_id="call-10")),
    )
    monkeypatch.setattr(
        worker,
        "AsyncSessionFactory",
        MagicMock(return_value=db_context),
    )
    monkeypatch.setattr(
        worker,
        "load_agent_session",
        AsyncMock(return_value=(training_session, db_scenario)),
    )
    monkeypatch.setattr(
        worker,
        "build_training_scenario",
        MagicMock(return_value=scenario),
    )
    monkeypatch.setattr(
        worker,
        "create_training_session",
        MagicMock(return_value=session),
    )
    monkeypatch.setattr(
        worker,
        "TrainingCustomer",
        MagicMock(return_value=MagicMock()),
    )
    monkeypatch.setattr(
        worker,
        "SessionEventRecorder",
        MagicMock(return_value=event_recorder),
    )
    monkeypatch.setattr(worker, "register_session_events", MagicMock())
    monkeypatch.setattr(worker, "register_transcript_events", MagicMock())
    monkeypatch.setattr(
        worker,
        "register_tool_execution_events",
        MagicMock(),
    )

    await worker.training_agent(ctx)

    # Capture and invoke the registered participant_connected callback.


    callback = registered_callbacks.get("participant_connected")
    assert callback is not None, "participant_connected callback was not registered"

    # The participant is first observed through the callback.
    callback(participant)

    # It is also present in remote_participants after session.start().
    # Both paths must produce only one event.
    matching_calls = [
        call
        for call in event_recorder.record.call_args_list
        if call.args[0] == SessionEventType.PARTICIPANT_JOINED
    ]

    assert len(matching_calls) == 1
    assert matching_calls[0].args[1] == {
        "identity": "trainee-1",
        "sid": "PA_test123",
        "room_name": "test-room",
    }
