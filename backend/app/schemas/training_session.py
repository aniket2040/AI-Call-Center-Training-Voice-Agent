from datetime import datetime

from pydantic import BaseModel, ConfigDict

from backend.app.models.enums import TrainingSessionStatus
from backend.app.schemas.common import PositiveID


class TrainingSessionCreate(BaseModel):
    """Request for creating a training session."""

    trainee_id: PositiveID
    scenario_id: PositiveID


class TrainingSessionResponse(BaseModel):
    """Public representation of a training session."""

    model_config = ConfigDict(from_attributes=True)

    id: PositiveID
    trainee_id: PositiveID
    scenario_id: PositiveID
    status: TrainingSessionStatus
    started_at: datetime | None = None
    ended_at: datetime | None = None