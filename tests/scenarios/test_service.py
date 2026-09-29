import pytest

from backend.app.db.session import AsyncSessionFactory
from backend.app.scenarios import (
    ScenarioInactiveError,
    ScenarioNotFoundError,
    ScenarioService,
)


def scenario_payload() -> dict:
    return {
        "name": "Refund - Angry Customer",
        "description": "Customer is waiting for a refund.",
        "difficulty": "medium",
        "persona_config": {
            "name": "Rahul",
            "mood": "frustrated",
            "patience": "low",
        },
        "rules_config": {
            "become_angry_if_ignored": True,
            "calm_if_handled_well": True,
            "situation": {
                "issue": "refund_not_received",
                "days_waiting": 14,
            },
        },
        "objectives": [
            "verify_customer",
            "show_empathy",
            "understand_problem",
            "provide_resolution",
        ],
        "evaluation_config": {
            "criteria": [
                "empathy",
                "communication",
                "problem_understanding",
                "resolution",
                "professionalism",
            ],
        },
    }


@pytest.mark.asyncio
async def test_create_and_get_scenario():
    async with AsyncSessionFactory() as session:
        service = ScenarioService(session)

        scenario = await service.create_scenario(
            **scenario_payload(),
        )

        await session.commit()

        loaded = await service.get_scenario(
            scenario_id=int(scenario.id),
        )

        assert loaded.name == "Refund - Angry Customer"
        assert loaded.difficulty == "medium"
        assert loaded.persona.name == "Rahul"
        assert loaded.situation.days_waiting == 14

        # Cleanup
        db_scenario = await service.repository.get_by_id(
            int(scenario.id),
        )

        await session.delete(db_scenario)
        await session.commit()


@pytest.mark.asyncio
async def test_inactive_scenario_is_rejected():
    async with AsyncSessionFactory() as session:
        service = ScenarioService(session)

        scenario = await service.create_scenario(
            **scenario_payload(),
            is_active=False,
        )

        await session.commit()

        with pytest.raises(ScenarioInactiveError):
            await service.get_scenario(
                scenario_id=int(scenario.id),
            )

        db_scenario = await service.repository.get_by_id(
            int(scenario.id),
        )

        await session.delete(db_scenario)
        await session.commit()


@pytest.mark.asyncio
async def test_missing_scenario_is_rejected():
    async with AsyncSessionFactory() as session:
        service = ScenarioService(session)

        with pytest.raises(ScenarioNotFoundError):
            await service.get_scenario(
                scenario_id=999999,
            )


@pytest.mark.asyncio
async def test_activate_and_deactivate_scenario():
    async with AsyncSessionFactory() as session:
        service = ScenarioService(session)

        scenario = await service.create_scenario(
            **scenario_payload(),
            is_active=False,
        )

        await session.commit()

        scenario_id = int(scenario.id)

        with pytest.raises(ScenarioInactiveError):
            await service.get_scenario(scenario_id)

        activated = await service.activate_scenario(
            scenario_id,
        )

        assert activated.name == "Refund - Angry Customer"

        loaded = await service.get_scenario(
            scenario_id,
            use_cache=True,
        )

        assert loaded.name == activated.name

        await service.deactivate_scenario(
            scenario_id,
        )

        await session.commit()

        with pytest.raises(ScenarioInactiveError):
            await service.get_scenario(
                scenario_id,
                use_cache=False,
            )

        db_scenario = await service.repository.get_by_id(
            scenario_id,
        )

        await session.delete(db_scenario)
        await session.commit()