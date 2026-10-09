from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PersonaConfig(BaseModel):
    """Customer persona used during the training scenario."""

    name: str = Field(
        min_length=1,
        max_length=255,
    )

    mood: str = Field(
        min_length=1,
        max_length=100,
    )

    patience: str = Field(
        min_length=1,
        max_length=100,
    )


class SituationConfig(BaseModel):
    """Situation presented to the trainee."""

    issue: str = Field(
        min_length=1,
        max_length=255,
    )

    days_waiting: int | None = Field(
        default=None,
        ge=0,
    )


class RulesConfig(BaseModel):
    """Behavioral rules for the scenario."""

    model_config = ConfigDict(extra="forbid")

    become_angry_if_ignored: bool = False
    calm_if_handled_well: bool = False

    escalate_if_repeated_failures: int | None = Field(
        default=None,
        ge=1,
    )
    escalate_if_patience_low: bool = False
    escalate_if_identity_verification_fails: bool = False



class EvaluationConfig(BaseModel):
    """Evaluation criteria for the scenario."""

    criteria: list[str] = Field(
        min_length=1,
    )


class ScenarioDefinition(BaseModel):
    """
    Internal representation of a training scenario.

    This is the object consumed by the scenario/conversation
    engine rather than the SQLAlchemy database model.
    """

    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    difficulty: str

    persona: PersonaConfig

    situation: SituationConfig

    objectives: list[str] = Field(
        min_length=1,
    )

    rules: RulesConfig

    evaluation: EvaluationConfig