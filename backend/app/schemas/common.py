from typing import Annotated

from pydantic import Field


PositiveID = Annotated[
    int,
    Field(gt=0),
]

Score = Annotated[
    float,
    Field(ge=0, le=100),
]

Difficulty = Annotated[
    str,
    Field(pattern=r"^(easy|medium|hard)$"),
]