
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.app.models.enums import TrainingSessionStatus
from backend.app.services.call_service import (
    CallService,
    CallDispatchError,
    TraineeNotFoundError,
    InvalidTraineeError,
    ScenarioNotFoundError,
    InactiveScenarioError,
)


@pytest.fixture
def call_service():
    db = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.rollback = AsyncMock()

    service = CallService(db)

    service.users = MagicMock()
    service.scenarios = MagicMock()
    service.sessions = MagicMock()
    service.lifecycle = MagicMock()
    service.events = MagicMock()
    service.dispatcher = MagicMock()

    service.users.get_by_id = AsyncMock()
    service.scenarios.get_by_id = AsyncMock()
    service.sessions.create = AsyncMock()

    service.lifecycle.transition = AsyncMock()
    service.events.create = AsyncMock()
    service.dispatcher.dispatch_agent = AsyncMock(
        return_value="dispatch-test-123"
    )

    return service, db


@pytest.mark.asyncio
async def test_create_call_success(call_service):
    service, db = call_service

    trainee = SimpleNamespace(id=1, role="trainee")
    scenario = SimpleNamespace(id=2, is_active=True)

    created_session = SimpleNamespace(
        id=10,
        trainee_id=1,
        scenario_id=2,
        status=TrainingSessionStatus.CREATED.value,
        livekit_room_name="training-test",
    )

    service.users.get_by_id.return_value = trainee
    service.scenarios.get_by_id.return_value = scenario
    service.sessions.create.return_value = created_session

    result = await service.create_call(
        trainee_id=1,
        scenario_id=2,
        phone_number="+919876543210",
    )

    assert result is created_session

    service.sessions.create.assert_awaited_once()

    kwargs = service.sessions.create.await_args.kwargs

    assert kwargs["trainee_id"] == 1
    assert kwargs["scenario_id"] == 2
    assert kwargs["phone_number"] == "+919876543210"
    assert kwargs["status"] == TrainingSessionStatus.CREATED.value
    assert kwargs["livekit_room_name"].startswith("training-")

    assert service.lifecycle.transition.await_count == 1

    transition_args = service.lifecycle.transition.await_args
    assert transition_args.args[0] == 10
    assert transition_args.args[1] == TrainingSessionStatus.DISPATCHING

    service.dispatcher.dispatch_agent.assert_awaited_once()

    dispatch_kwargs = service.dispatcher.dispatch_agent.await_args.kwargs
    assert dispatch_kwargs["session_id"] == 10
    assert dispatch_kwargs["scenario_id"] == 2
    assert dispatch_kwargs["room_name"] == kwargs["livekit_room_name"]
    assert dispatch_kwargs["room_name"].startswith("training-")

    service.events.create.assert_awaited_once()

    event_kwargs = service.events.create.await_args.kwargs
    assert event_kwargs["session_id"] == 10
    assert event_kwargs["event_type"] == "agent_dispatched"
    assert event_kwargs["payload"]["dispatch_id"] == "dispatch-test-123"

    assert db.commit.await_count == 3
    assert db.refresh.await_count == 2

    db.refresh.assert_has_awaits(
        [
            ((created_session,),),
            ((created_session,),),
        ]
    )
    db.rollback.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_call_dispatch_failure(call_service):
    service, db = call_service

    from backend.app.services.livekit_dispatch import LiveKitDispatchError

    service.users.get_by_id.return_value = SimpleNamespace(
        id=1,
        role="trainee",
    )
    service.scenarios.get_by_id.return_value = SimpleNamespace(
        id=2,
        is_active=True,
    )
    service.sessions.create.return_value = SimpleNamespace(
        id=10,
        trainee_id=1,
        scenario_id=2,
        status=TrainingSessionStatus.CREATED.value,
        livekit_room_name="training-test",
    )

    service.dispatcher.dispatch_agent.side_effect = LiveKitDispatchError(
        "LiveKit unavailable"
    )

    with pytest.raises(CallDispatchError):
        await service.create_call(
            trainee_id=1,
            scenario_id=2,
            phone_number="+919876543210",
        )

    assert service.lifecycle.transition.await_count == 2

    transitions = service.lifecycle.transition.await_args_list

    assert transitions[0].args[1] == TrainingSessionStatus.DISPATCHING
    assert transitions[1].args[1] == TrainingSessionStatus.FAILED

    service.events.create.assert_not_awaited()
    db.rollback.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_call_rejects_missing_trainee(call_service):
    service, db = call_service

    service.users.get_by_id.return_value = None

    with pytest.raises(TraineeNotFoundError):
        await service.create_call(
            trainee_id=999,
            scenario_id=2,
            phone_number="+918873686521",
        )

    service.scenarios.get_by_id.assert_not_awaited()
    service.sessions.create.assert_not_awaited()
    service.dispatcher.dispatch_agent.assert_not_awaited()
    db.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_call_rejects_non_trainee_user(call_service):
    service, db = call_service

    service.users.get_by_id.return_value = SimpleNamespace(
        id=1,
        role="admin",
    )

    with pytest.raises(InvalidTraineeError):
        await service.create_call(
            trainee_id=1,
            scenario_id=2,
            phone_number="+919876543210",
        )

    service.scenarios.get_by_id.assert_not_awaited()
    service.sessions.create.assert_not_awaited()
    service.dispatcher.dispatch_agent.assert_not_awaited()
    db.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_call_rejects_missing_scenario(call_service):
    service, db = call_service

    service.users.get_by_id.return_value = SimpleNamespace(
        id=1,
        role="trainee",
    )
    service.scenarios.get_by_id.return_value = None

    with pytest.raises(ScenarioNotFoundError):
        await service.create_call(
            trainee_id=1,
            scenario_id=999,
            phone_number="+919876543210",
        )

    service.sessions.create.assert_not_awaited()
    service.dispatcher.dispatch_agent.assert_not_awaited()
    db.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_call_rejects_inactive_scenario(call_service):
    service, db = call_service

    service.users.get_by_id.return_value = SimpleNamespace(
        id=1,
        role="trainee",
    )
    service.scenarios.get_by_id.return_value = SimpleNamespace(
        id=2,
        is_active=False,
    )

    with pytest.raises(InactiveScenarioError):
        await service.create_call(
            trainee_id=1,
            scenario_id=2,
            phone_number="+919876543210",
        )

    service.sessions.create.assert_not_awaited()
    service.dispatcher.dispatch_agent.assert_not_awaited()
    db.commit.assert_not_awaited()