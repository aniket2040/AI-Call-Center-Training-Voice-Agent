from datetime import datetime, timezone
from backend.app.agents.state.events import SessionEventType
import pytest

from backend.app.db.session import AsyncSessionFactory
from backend.app.repositories import (
    ScenarioRepository,
    SessionEventRepository,
    TrainingSessionRepository,
    UserRepository,
)


@pytest.mark.asyncio
async def test_create_and_get_session_event():
    async with AsyncSessionFactory() as session:
        user_repository = UserRepository(session)
        scenario_repository = ScenarioRepository(session)
        training_session_repository = TrainingSessionRepository(session)
        event_repository = SessionEventRepository(session)

        user = await user_repository.create(
            name="Event Test Trainee",
            phone_number="+917777777777",
        )

        scenario = await scenario_repository.create(
            name="Event Test Scenario",
            description="Scenario for session event testing.",
            difficulty="easy",
            persona_config={
                "role": "customer",
            },
            rules_config={},
            objectives=[
                "Test conversation event handling",
            ],
            evaluation_config={},
        )

        await session.flush()

        training_session = await training_session_repository.create(
            trainee_id=user.id,
            scenario_id=scenario.id,
            livekit_room_name="event-test-room-001",
        )

        await session.flush()

        event = await event_repository.create(
            session_id=training_session.id,
            event_type=SessionEventType.CONVERSATION_STARTED,
            event_timestamp=datetime.now(timezone.utc),
            payload={
                "source": "test",
                "message": "Conversation started",
            },
        )

        await session.commit()

        assert event.id is not None
        assert event.session_id == training_session.id
        assert event.event_type == "CONVERSATION_STARTED"
        assert event.payload["source"] == "test"

        fetched = await event_repository.get_by_id(event.id)

        assert fetched is not None
        assert fetched.id == event.id

        events = await event_repository.list_by_session(
            training_session.id
        )

        assert any(
            item.id == event.id
            for item in events
        )

        await session.delete(training_session)
        await session.delete(scenario)
        await session.delete(user)
        await session.commit()