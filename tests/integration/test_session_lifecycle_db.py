
import os
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from backend.app.lifecycle.service import SessionLifecycleService
from backend.app.models import (
    Scenario,
    SessionEvent,
    TrainingSession,
    TrainingSessionStatus,
    User,
)


TEST_DATABASE_NAME = "ai_call_center_test"


@pytest_asyncio.fixture
async def db_session():
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        pytest.fail(
            "DATABASE_URL must explicitly point to ai_call_center_test."
        )

    test_engine = create_async_engine(
        database_url,
        pool_pre_ping=True,
    )

    try:
        async with test_engine.connect() as connection:
            result = await connection.execute(
                text("SELECT current_database()")
            )
            actual_database = result.scalar_one()

            if actual_database != TEST_DATABASE_NAME:
                pytest.fail(
                    f"Unsafe database target: {actual_database}. "
                    f"Expected: {TEST_DATABASE_NAME}."
                )

        async with test_engine.connect() as connection:
            transaction = await connection.begin()

            test_session_factory = async_sessionmaker(
                bind=connection,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=False,
            )

            async with test_session_factory() as session:
                try:
                    yield session
                finally:
                    await session.close()

            await transaction.rollback()

    finally:
        await test_engine.dispose()


@pytest.mark.asyncio
async def test_lifecycle_transition_persists_status_and_event(
    db_session: AsyncSession,
):
    unique_id = uuid4().hex

    user = User(
        name="Lifecycle Integration Test",
        phone_number=f"9{unique_id[:9]}",
        role="trainee",
    )

    scenario = Scenario(
        name=f"Lifecycle Test Scenario {unique_id}",
        description="Temporary integration test scenario",
        difficulty="beginner",
        persona_config={},
        rules_config={},
        objectives=["Test lifecycle transition"],
        evaluation_config={},
        is_active=True,
    )

    db_session.add_all([user, scenario])
    await db_session.flush()

    training_session = TrainingSession(
        trainee_id=user.id,
        scenario_id=scenario.id,
        livekit_room_name=f"lifecycle-test-{unique_id}",
        status=TrainingSessionStatus.CREATED.value,
    )

    db_session.add(training_session)
    await db_session.flush()

    lifecycle = SessionLifecycleService(db_session)

    updated_session = await lifecycle.transition(
        training_session.id,
        TrainingSessionStatus.DISPATCHING,
        reason="Integration test dispatch",
    )

    assert updated_session.status == TrainingSessionStatus.DISPATCHING.value

    persisted_session = await db_session.get(
        TrainingSession,
        training_session.id,
        populate_existing=True,
    )

    assert persisted_session is not None
    assert persisted_session.status == TrainingSessionStatus.DISPATCHING.value

    event_result = await db_session.execute(
        select(SessionEvent).where(
            SessionEvent.session_id == training_session.id,
            SessionEvent.event_type == "lifecycle_transition",
        )
    )

    event = event_result.scalar_one()

    assert event.payload == {
        "from_status": "created",
        "to_status": "dispatching",
        "reason": "Integration test dispatch",
    }