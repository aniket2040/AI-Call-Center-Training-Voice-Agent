from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services.call_service import (
    TraineeNotFoundError,
    InvalidTraineeError,
    ScenarioNotFoundError,
    InactiveScenarioError,
)


client = TestClient(app)


def test_create_call_success():
    mock_session = type(
        "MockSession",
        (),
        {
            "id": 101,
            "status": "created",
        },
    )()

    with patch(
        "backend.app.api.v1.calls.CallService"
    ) as mock_service_class:
        mock_service = mock_service_class.return_value
        mock_service.create_call = AsyncMock(return_value=mock_session)

        response = client.post(
            "/api/v1/calls",
            json={
                "trainee_id": 1,
                "scenario_id": 1,
                "phone_number": "+919876543210",
            },
        )

    assert response.status_code == 201
    assert response.json() == {
        "session_id": 101,
        "status": "created",
    }


def test_create_call_trainee_not_found():
    with patch(
        "backend.app.api.v1.calls.CallService"
    ) as mock_service_class:
        mock_service = mock_service_class.return_value
        mock_service.create_call = AsyncMock(
            side_effect=TraineeNotFoundError("Trainee not found")
        )

        response = client.post(
            "/api/v1/calls",
            json={
                "trainee_id": 999,
                "scenario_id": 1,
                "phone_number": "+919876543210",
            },
        )

    assert response.status_code == 404


def test_create_call_invalid_trainee():
    with patch(
        "backend.app.api.v1.calls.CallService"
    ) as mock_service_class:
        mock_service = mock_service_class.return_value
        mock_service.create_call = AsyncMock(
            side_effect=InvalidTraineeError("User is not a trainee")
        )

        response = client.post(
            "/api/v1/calls",
            json={
                "trainee_id": 1,
                "scenario_id": 1,
                "phone_number": "+919876543210",
            },
        )

    assert response.status_code == 400


def test_create_call_scenario_not_found():
    with patch(
        "backend.app.api.v1.calls.CallService"
    ) as mock_service_class:
        mock_service = mock_service_class.return_value
        mock_service.create_call = AsyncMock(
            side_effect=ScenarioNotFoundError("Scenario not found")
        )

        response = client.post(
            "/api/v1/calls",
            json={
                "trainee_id": 1,
                "scenario_id": 999,
                "phone_number": "+919876543210",
            },
        )

    assert response.status_code == 404


def test_create_call_inactive_scenario():
    with patch(
        "backend.app.api.v1.calls.CallService"
    ) as mock_service_class:
        mock_service = mock_service_class.return_value
        mock_service.create_call = AsyncMock(
            side_effect=InactiveScenarioError("Scenario is inactive")
        )

        response = client.post(
            "/api/v1/calls",
            json={
                "trainee_id": 1,
                "scenario_id": 1,
                "phone_number": "+919876543210",
            },
        )

    assert response.status_code == 409


def test_create_call_invalid_phone_number():
    response = client.post(
        "/api/v1/calls",
        json={
            "trainee_id": 1,
            "scenario_id": 1,
            "phone_number": "invalid",
        },
    )

    assert response.status_code == 422
