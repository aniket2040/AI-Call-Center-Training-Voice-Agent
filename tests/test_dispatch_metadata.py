
import json

import pytest

from backend.app.agents.dispatch_metadata import (
    DispatchMetadata,
    InvalidDispatchMetadataError,
    parse_dispatch_metadata,
)


def test_parse_valid_dispatch_metadata():
    raw = json.dumps({
        "session_id": 10,
        "scenario_id": 2,
        "trainee_id": 1,
        "call_id": "10",
    })

    result = parse_dispatch_metadata(raw)

    assert result == DispatchMetadata(
        session_id=10,
        scenario_id=2,
        trainee_id=1,
        call_id="10",
    )


@pytest.mark.parametrize(
    "raw",
    [
        None,
        "",
        "not-json",
        "[]",
        "{}",
        json.dumps({
            "session_id": 10,
            "scenario_id": 2,
            "trainee_id": 1,
        }),
        json.dumps({
            "session_id": True,
            "scenario_id": 2,
            "trainee_id": 1,
            "call_id": "10",
        }),
        json.dumps({
            "session_id": 10,
            "scenario_id": 0,
            "trainee_id": 1,
            "call_id": "10",
        }),
        json.dumps({
            "session_id": 10,
            "scenario_id": 2,
            "trainee_id": 1,
            "call_id": " ",
        }),
    ],
)
def test_reject_invalid_dispatch_metadata(raw):
    with pytest.raises(InvalidDispatchMetadataError):
        parse_dispatch_metadata(raw)
