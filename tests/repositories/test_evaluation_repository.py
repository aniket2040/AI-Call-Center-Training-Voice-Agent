import pytest

from backend.app.db.session import AsyncSessionFactory
from backend.app.repositories import (
    EvaluationRepository,
    ScenarioRepository,
    TrainingSessionRepository,
    UserRepository,
)


@pytest.mark.asyncio
async def test_create_and_update_evaluation():
    async with AsyncSessionFactory() as session:
        user_repository = UserRepository(session)
        scenario_repository = ScenarioRepository(session)
        training_session_repository = TrainingSessionRepository(session)
        evaluation_repository = EvaluationRepository(session)

        user = await user_repository.create(
            name="Evaluation Test Trainee",
            phone_number="+916666666666",
        )

        scenario = await scenario_repository.create(
            name="Evaluation Test Scenario",
            description="Scenario for evaluation testing.",
            difficulty="medium",
            persona_config={
                "role": "customer",
            },
            rules_config={},
            objectives=[
                "Resolve customer issue",
                "Communicate clearly",
            ],
            evaluation_config={
                "communication": 50,
                "problem_solving": 50,
            },
        )

        await session.flush()

        training_session = await training_session_repository.create(
            trainee_id=user.id,
            scenario_id=scenario.id,
            livekit_room_name="evaluation-test-room-001",
        )

        await session.flush()

        evaluation = await evaluation_repository.create(
            session_id=training_session.id,
            model="test-evaluation-model",
        )

        await session.commit()

        assert evaluation.id is not None
        assert evaluation.session_id == training_session.id
        assert evaluation.status == "pending"
        assert evaluation.model == "test-evaluation-model"

        fetched = await evaluation_repository.get_by_id(
            evaluation.id
        )

        assert fetched is not None
        assert fetched.id == evaluation.id

        fetched_by_session = await evaluation_repository.get_by_session_id(
            training_session.id
        )

        assert fetched_by_session is not None
        assert fetched_by_session.id == evaluation.id

        updated = await evaluation_repository.update_result(
            evaluation,
            status="completed",
            overall_score=87.50,
            criteria_scores={
                "communication": 90,
                "problem_solving": 85,
            },
            evidence=[
                {
                    "criterion": "communication",
                    "timestamp": 12.5,
                    "reason": "Clear explanation",
                }
            ],
            strengths=[
                "Good communication",
                "Professional tone",
            ],
            weaknesses=[
                "Could ask more clarifying questions",
            ],
            feedback="Good overall performance.",
            model="test-evaluation-model-v2",
        )

        await session.commit()

        assert updated.status == "completed"
        assert float(updated.overall_score) == 87.50
        assert updated.criteria_scores["communication"] == 90
        assert len(updated.evidence) == 1
        assert len(updated.strengths) == 2
        assert len(updated.weaknesses) == 1
        assert updated.feedback == "Good overall performance."
        assert updated.model == "test-evaluation-model-v2"

        await session.delete(training_session)
        await session.delete(scenario)
        await session.delete(user)
        await session.commit()