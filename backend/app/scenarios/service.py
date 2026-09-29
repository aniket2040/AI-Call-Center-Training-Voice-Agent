from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.repositories.scenario import ScenarioRepository
from backend.app.scenarios.loader import ScenarioLoader
from backend.app.scenarios.models import ScenarioDefinition


class ScenarioService:
    """
    Application service for managing training scenarios.

    Responsibilities:
    - Create scenarios
    - Load validated scenarios
    - Update scenarios
    - Activate/deactivate scenarios
    - Maintain a small in-process cache
    """

    def __init__(self, session: AsyncSession) -> None:
        self.repository = ScenarioRepository(session)
        self.loader = ScenarioLoader(session)

    async def get_scenario(
        self,
        scenario_id: int,
        *,
        use_cache: bool = True,
    ) -> ScenarioDefinition:
        if use_cache and scenario_id in _SCENARIO_CACHE:
            return _SCENARIO_CACHE[scenario_id]

        scenario = await self.loader.load(scenario_id)

        if use_cache:
            _SCENARIO_CACHE[scenario_id] = scenario

        return scenario

    async def create_scenario(
        self,
        *,
        name: str,
        description: str,
        difficulty: str,
        persona_config: dict[str, Any],
        rules_config: dict[str, Any],
        objectives: list[str],
        evaluation_config: dict[str, Any],
        is_active: bool = True,
    ) -> ScenarioDefinition:

        scenario = await self.repository.create(
            name=name,
            description=description,
            difficulty=difficulty,
            persona_config=persona_config,
            rules_config=rules_config,
            objectives=objectives,
            evaluation_config=evaluation_config,
            is_active=is_active,
        )

        scenario_definition = await self.loader.load(
            scenario.id,
            require_active=False,
        )

        if is_active:
            _SCENARIO_CACHE[scenario.id] = scenario_definition

        return scenario_definition

    async def update_scenario(
        self,
        scenario_id: int,
        *,
        name: str | None = None,
        description: str | None = None,
        difficulty: str | None = None,
        persona_config: dict[str, Any] | None = None,
        rules_config: dict[str, Any] | None = None,
        objectives: list[str] | None = None,
        evaluation_config: dict[str, Any] | None = None,
    ) -> ScenarioDefinition:

        scenario = await self.repository.get_by_id(scenario_id)

        if scenario is None:
            raise LookupError(
                f"Scenario {scenario_id} was not found."
            )

        if name is not None:
            scenario.name = name

        if description is not None:
            scenario.description = description

        if difficulty is not None:
            scenario.difficulty = difficulty

        if persona_config is not None:
            scenario.persona_config = persona_config

        if rules_config is not None:
            scenario.rules_config = rules_config

        if objectives is not None:
            scenario.objectives = objectives

        if evaluation_config is not None:
            scenario.evaluation_config = evaluation_config

        await self.repository.session.flush()

        _SCENARIO_CACHE.pop(scenario_id, None)

        return await self.loader.load(
            scenario_id,
            require_active=False,
        )

    async def activate_scenario(
        self,
        scenario_id: int,
    ) -> ScenarioDefinition:

        scenario = await self.repository.get_by_id(scenario_id)

        if scenario is None:
            raise LookupError(
                f"Scenario {scenario_id} was not found."
            )

        scenario.is_active = True

        await self.repository.session.flush()

        _SCENARIO_CACHE.pop(scenario_id, None)

        scenario_definition = await self.loader.load(
            scenario_id,
            require_active=True,
        )

        _SCENARIO_CACHE[scenario_id] = scenario_definition

        return scenario_definition

    async def deactivate_scenario(
        self,
        scenario_id: int,
    ) -> None:

        scenario = await self.repository.get_by_id(scenario_id)

        if scenario is None:
            raise LookupError(
                f"Scenario {scenario_id} was not found."
            )

        scenario.is_active = False

        await self.repository.session.flush()

        _SCENARIO_CACHE.pop(scenario_id, None)


_SCENARIO_CACHE: dict[int, ScenarioDefinition] = {}