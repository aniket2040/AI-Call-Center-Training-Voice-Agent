from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from backend.app.schemas.common import Difficulty, PositiveID


class ScenarioCreate(BaseModel):
    """Request for creating a training scenario."""

    name: str = Field(
        min_length=1,
        max_length=255,
    )

    description: str = Field(
        min_length=1,
        max_length=5000,
    )

    difficulty: Difficulty

    persona_config: dict[str, Any] = Field(
        default_factory=dict,
    )

    rules_config: dict[str, Any] = Field(
        default_factory=dict,
    )

    objectives: list[str] = Field(
        min_length=1,
    )

    evaluation_config: dict[str, Any] = Field(
        default_factory=dict,
    )


class ScenarioResponse(BaseModel):
    """Public representation of a scenario."""

    model_config = ConfigDict(from_attributes=True)

    id: PositiveID
    name: str
    description: str
    difficulty: Difficulty
    objectives: list[str]
    is_active: bool