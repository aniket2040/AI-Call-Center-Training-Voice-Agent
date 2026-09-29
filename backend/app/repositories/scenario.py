from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models import Scenario


class ScenarioRepository:
    """Database operations for training scenarios."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, scenario_id: int) -> Scenario | None:
        result = await self.session.execute(
            select(Scenario).where(Scenario.id == scenario_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Scenario | None:
        result = await self.session.execute(
            select(Scenario).where(Scenario.name == name)
        )
        return result.scalar_one_or_none()

    async def list_active(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Scenario]:
        result = await self.session.execute(
            select(Scenario)
            .where(Scenario.is_active.is_(True))
            .order_by(Scenario.id)
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def create(
        self,
        *,
        name: str,
        description: str,
        difficulty: str,
        persona_config: dict,
        rules_config: dict,
        objectives: list[str],
        evaluation_config: dict,
        is_active: bool = True,
    ) -> Scenario:
        scenario = Scenario(
            name=name,
            description=description,
            difficulty=difficulty,
            persona_config=persona_config,
            rules_config=rules_config,
            objectives=objectives,
            evaluation_config=evaluation_config,
            is_active=is_active,
        )

        self.session.add(scenario)
        await self.session.flush()

        return scenario