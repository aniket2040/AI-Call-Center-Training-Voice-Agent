from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from backend.app.schemas.common import PositiveID


class SessionEventCreate(BaseModel):
    """Request for creating a session event."""

    session_id: PositiveID

    event_type: str = Field(
        min_length=1,
        max_length=100,
    )

    event_timestamp: datetime

    payload: dict[str, Any] = Field(
        default_factory=dict,
    )


class SessionEventResponse(BaseModel):
    """Public representation of a session event."""

    model_config = ConfigDict(from_attributes=True)

    id: PositiveID
    session_id: PositiveID
    event_type: str
    event_timestamp: datetime
    payload: dict[str, Any]