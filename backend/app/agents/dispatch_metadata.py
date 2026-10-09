
from dataclasses import dataclass
import json
from typing import Any


class InvalidDispatchMetadataError(ValueError):
    """Raised when agent dispatch metadata is invalid."""


@dataclass(frozen=True)
class DispatchMetadata:
    session_id: int
    scenario_id: int
    trainee_id: int
    call_id: str


def parse_dispatch_metadata(raw_metadata: str | None) -> DispatchMetadata:
    if not raw_metadata:
        raise InvalidDispatchMetadataError(
            "Dispatch metadata is missing."
        )

    try:
        data: Any = json.loads(raw_metadata)
    except (json.JSONDecodeError, TypeError) as exc:
        raise InvalidDispatchMetadataError(
            "Dispatch metadata must be valid JSON."
        ) from exc

    if not isinstance(data, dict):
        raise InvalidDispatchMetadataError(
            "Dispatch metadata must be a JSON object."
        )

    required_fields = (
        "session_id",
        "scenario_id",
        "trainee_id",
        "call_id",
    )

    missing_fields = [
        field for field in required_fields
        if field not in data
    ]
    if missing_fields:
        raise InvalidDispatchMetadataError(
            f"Missing metadata fields: {', '.join(missing_fields)}."
        )

    for field in ("session_id", "scenario_id", "trainee_id"):
        value = data[field]

        # bool is a subclass of int in Python, so reject it explicitly.
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise InvalidDispatchMetadataError(
                f"'{field}' must be a positive integer."
            )

    call_id = data["call_id"]
    if not isinstance(call_id, str) or not call_id.strip():
        raise InvalidDispatchMetadataError(
            "'call_id' must be a non-empty string."
        )

    return DispatchMetadata(
        session_id=data["session_id"],
        scenario_id=data["scenario_id"],
        trainee_id=data["trainee_id"],
        call_id=call_id,
    )