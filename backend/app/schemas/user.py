from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    """Public request for creating a trainee."""

    name: str = Field(
        min_length=1,
        max_length=255,
    )

    phone_number: str = Field(
        min_length=10,
        max_length=15,
        pattern=r"^\+?[1-9]\d{9,14}$",
    )


class UserResponse(BaseModel):
    """Public representation of a user."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    phone_number: str
    role: str