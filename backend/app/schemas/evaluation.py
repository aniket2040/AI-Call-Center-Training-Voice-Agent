from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from backend.app.models.enums import EvaluationStatus
from backend.app.schemas.common import PositiveID, Score


class EvaluationCreate(BaseModel):
    """Request for creating an evaluation."""

    session_id: PositiveID
    model: str | None = Field(
        default=None,
        max_length=255,
    )


class EvaluationResponse(BaseModel):
    """Public representation of an evaluation."""

    model_config = ConfigDict(from_attributes=True)

    id: PositiveID
    session_id: PositiveID
    status: EvaluationStatus
    overall_score: Score | None = None
    criteria_scores: dict[str, Any]
    strengths: list[str]
    weaknesses: list[str]
    feedback: str | None = None