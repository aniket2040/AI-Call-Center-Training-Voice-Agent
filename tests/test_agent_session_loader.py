
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from backend.app.agents.session_loader import build_training_scenario
from backend.app.agents.dispatch_metadata import DispatchMetadata
from backend.app.agents.session_loader import (
    AgentSessionValidationError,
    load_agent_session,
)
from backend.app.models.scenario import Scenario
from backend.app.models.training_session import TrainingSession


@pytest.fixture
def metadata():
    return DispatchMetadata(
        session_id=10,
        scenario_id=2,
        trainee_id=1,
        call_id="10",
    )


@pytest.fixture
def training_session():
    return SimpleNamespace(
        id=10,
        trainee_id=1,
        scenario_id=2,
        livekit_room_name="training-test",
    )


@pytest.fixture
def scenario():
    return SimpleNamespace(
        id=2,
        is_active=True,
    )


@pytest.mark.asyncio
async def test_load_agent_session_success(
    metadata,
    training_session,
    scenario,
):
    db = SimpleNamespace(
        get=AsyncMock(side_effect=[training_session, scenario])
    )

    session, loaded_scenario = await load_agent_session(
        db,
        metadata,
        room_name="training-test",
    )

    assert session is training_session
    assert loaded_scenario is scenario
    assert db.get.await_count == 2


@pytest.mark.asyncio
async def test_reject_mismatched_trainee(
    metadata,
    training_session,
):
    training_session.trainee_id = 99
    db = SimpleNamespace(get=AsyncMock(return_value=training_session))

    with pytest.raises(
        AgentSessionValidationError,
        match="Trainee ID does not match",
    ):
        await load_agent_session(
            db,
            metadata,
            room_name="training-test",
        )

    assert db.get.await_count == 1


@pytest.mark.asyncio
async def test_reject_mismatched_room(
    metadata,
    training_session,
):
    db = SimpleNamespace(get=AsyncMock(return_value=training_session))

    with pytest.raises(
        AgentSessionValidationError,
        match="LiveKit room does not match",
    ):
        await load_agent_session(
            db,
            metadata,
            room_name="different-room",
        )


@pytest.mark.asyncio
async def test_reject_inactive_scenario(
    metadata,
    training_session,
    scenario,
):
    scenario.is_active = False
    db = SimpleNamespace(
        get=AsyncMock(side_effect=[training_session, scenario])
    )

    with pytest.raises(
        AgentSessionValidationError,
        match="Scenario is inactive",
    ):
        await load_agent_session(
            db,
            metadata,
            room_name="training-test",
        )


@pytest.mark.asyncio
async def test_reject_missing_session(metadata):
    db = SimpleNamespace(get=AsyncMock(return_value=None))

    with pytest.raises(
        AgentSessionValidationError,
        match="Training session does not exist",
    ):
        await load_agent_session(
            db,
            metadata,
            room_name="training-test",
        )




def test_build_training_scenario_success(scenario):
    scenario.name = "Order Delay"
    scenario.persona_config = {
        "persona": "Frustrated but reasonable customer",
        "situation": "The customer's order has not arrived.",
    }
    scenario.rules_config = {
        "rules": [
            "Start slightly frustrated.",
            "Become calmer when shown empathy.",
        ],
    }
    scenario.objectives = ["Understand the issue.", "Show empathy."]

    result = build_training_scenario(scenario)

    assert result.scenario_id == scenario.id
    assert result.name == "Order Delay"
    assert result.persona == "Frustrated but reasonable customer"
    assert result.situation == "The customer's order has not arrived."
    assert result.rules == scenario.rules_config["rules"]
    assert result.objectives == scenario.objectives


def test_build_training_scenario_rejects_missing_persona(scenario):
    scenario.persona_config = {
        "situation": "The customer's order has not arrived.",
    }
    scenario.rules_config = {"rules": ["Show empathy."]}
    scenario.objectives = ["Understand the issue."]

    with pytest.raises(
        AgentSessionValidationError,
        match="valid persona",
    ):
        build_training_scenario(scenario)


def test_build_training_scenario_rejects_invalid_rules(scenario):
    scenario.persona_config = {
        "persona": "Frustrated customer",
        "situation": "The order is late.",
    }
    scenario.rules_config = {"rules": "Show empathy"}
    scenario.objectives = ["Understand the issue."]

    with pytest.raises(
        AgentSessionValidationError,
        match="list of non-empty strings",
    ):
        build_training_scenario(scenario)