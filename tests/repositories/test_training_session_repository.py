import pytest

from backend.app.db.session import AsyncSessionFactory
from backend.app.repositories import (
    ScenarioRepository,
    TrainingSessionRepository,
    UserRepository,
)


@pytest.mark.asyncio
async def test_create_and_get_training_session():
    async with AsyncSessionFactory() as session:
        user_repository = UserRepository(session)
        scenario_repository = ScenarioRepository(session)
        session_repository = TrainingSessionRepository(session)

        user = await user_repository.create(
            name="Test Trainee",
            phone_number="+918888888888",
        )

        scenario = await scenario_repository.create(
            name="Test Support Call",
            description="Customer needs help with an order.",
            difficulty="easy",
            persona_config={
                "role": "customer",
                "tone": "neutral",
            },
            rules_config={},
            objectives=[
                "Understand the problem",
                "Provide a solution",
            ],
            evaluation_config={
                "communication": 50,
                "problem_solving": 50,
            },
        )

        await session.flush()

        training_session = await session_repository.create(
            trainee_id=user.id,
            scenario_id=scenario.id,
            livekit_room_name="test-training-room-001",
            livekit_participant_id="test-participant-001",
            phone_number="+918888888888",
        )

        await session.commit()

        assert training_session.id is not None
        assert training_session.trainee_id == user.id
        assert training_session.scenario_id == scenario.id
        assert training_session.livekit_room_name == "test-training-room-001"
        assert training_session.status == "created"

        fetched = await session_repository.get_by_id(
            training_session.id
        )

        assert fetched is not None
        assert fetched.id == training_session.id

        fetched_by_room = await session_repository.get_by_room_name(
            "test-training-room-001"
        )

        assert fetched_by_room is not None
        assert fetched_by_room.id == training_session.id

        trainee_sessions = await session_repository.list_by_trainee(
            user.id
        )

        assert any(
            item.id == training_session.id
            for item in trainee_sessions
        )

        updated = await session_repository.update_status(
            training_session,
            "in_progress",
        )

        await session.commit()

        assert updated.status == "in_progress"

        await session.delete(training_session)
        await session.delete(scenario)
        await session.delete(user)
        await session.commit()