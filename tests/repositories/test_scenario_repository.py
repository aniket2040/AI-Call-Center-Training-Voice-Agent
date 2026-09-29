import pytest

from backend.app.db.session import AsyncSessionFactory
from backend.app.repositories import ScenarioRepository


@pytest.mark.asyncio
async def test_create_and_get_scenario():
    async with AsyncSessionFactory() as session:
        repository = ScenarioRepository(session)

        scenario = await repository.create(
            name="Test Customer Complaint",
            description="Customer is unhappy about a delayed order.",
            difficulty="medium",
            persona_config={
                "role": "angry_customer",
                "tone": "frustrated",
            },
            rules_config={
                "max_hints": 2,
            },
            objectives=[
                "Understand the customer issue",
                "Apologize appropriately",
                "Offer a resolution",
            ],
            evaluation_config={
                "empathy": 30,
                "problem_solving": 40,
                "communication": 30,
            },
        )

        await session.commit()

        assert scenario.id is not None
        assert scenario.name == "Test Customer Complaint"
        assert scenario.difficulty == "medium"
        assert scenario.is_active is True

        fetched = await repository.get_by_id(scenario.id)

        assert fetched is not None
        assert fetched.id == scenario.id
        assert fetched.name == "Test Customer Complaint"

        fetched_by_name = await repository.get_by_name(
            "Test Customer Complaint"
        )

        assert fetched_by_name is not None
        assert fetched_by_name.id == scenario.id

        active_scenarios = await repository.list_active()

        assert any(
            item.id == scenario.id
            for item in active_scenarios
        )

        await session.delete(fetched)
        await session.commit()