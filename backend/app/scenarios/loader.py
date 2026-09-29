from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.repositories.scenario import ScenarioRepository
from backend.app.scenarios.models import ScenarioDefinition
from backend.app.scenarios.validator import validate_scenario


class ScenarioNotFoundError(LookupError):
    """Raised when a requested scenario does not exist."""


class ScenarioInactiveError(ValueError):
    """Raised when an inactive scenario is requested."""


class ScenarioLoader:
    """Loads and validates scenarios from PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        self.repository = ScenarioRepository(session)

    async def load(
        self,
        scenario_id: int,
        *,
        require_active: bool = True,
    ) -> ScenarioDefinition:
        scenario = await self.repository.get_by_id(scenario_id)

        if scenario is None:
            raise ScenarioNotFoundError(
                f"Scenario {scenario_id} was not found."
            )

        if require_active and not scenario.is_active:
            raise ScenarioInactiveError(
                f"Scenario {scenario_id} is inactive."
            )

        return validate_scenario(scenario)