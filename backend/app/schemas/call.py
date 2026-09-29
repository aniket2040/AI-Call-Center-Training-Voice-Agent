from pydantic import BaseModel, Field

from backend.app.schemas.common import PositiveID


class CallRequest(BaseModel):
    """Request to initiate a training call."""

    trainee_id: PositiveID
    scenario_id: PositiveID

    phone_number: str = Field(
        min_length=10,
        max_length=15,
        pattern=r"^\+?[1-9]\d{9,14}$",
    )


class CallResponse(BaseModel):
    """Response after a call has been initiated."""

    session_id: PositiveID
    status: str