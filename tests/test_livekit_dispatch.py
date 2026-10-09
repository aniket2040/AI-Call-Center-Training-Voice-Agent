
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.app.services.livekit_dispatch import (
    LiveKitDispatchError,
    LiveKitDispatchService,
)


@pytest.mark.asyncio
async def test_dispatch_agent_success():
    service = LiveKitDispatchService()

    mock_dispatch = MagicMock()
    mock_dispatch.id = "dispatch-123"

    mock_livekit_api = MagicMock()
    mock_livekit_api.agent_dispatch.create_dispatch = AsyncMock(
        return_value=mock_dispatch
    )

    mock_context = MagicMock()
    mock_context.__aenter__ = AsyncMock(return_value=mock_livekit_api)
    mock_context.__aexit__ = AsyncMock(return_value=None)

    with patch(
        "backend.app.services.livekit_dispatch.api.LiveKitAPI",
        return_value=mock_context,
    ):
        dispatch_id = await service.dispatch_agent(
            room_name="training-test-room",
            session_id=101,
            scenario_id=5,
            trainee_id=1,
            call_id="10",
        )

    assert dispatch_id == "dispatch-123"

    request = (
        mock_livekit_api.agent_dispatch.create_dispatch.call_args.args[0]
    )

    assert request.agent_name == "call-center-training-agent"
    assert request.room == "training-test-room"


@pytest.mark.asyncio
async def test_dispatch_agent_rejects_missing_credentials():
    service = LiveKitDispatchService()

    with patch(
        "backend.app.services.livekit_dispatch.settings.livekit_api_key",
        "",
    ):
        with pytest.raises(
            LiveKitDispatchError,
            match="credentials are not configured",
        ):
            await service.dispatch_agent(
                room_name="training-test-room",
                session_id=101,
                scenario_id=5,
                trainee_id=1,
                call_id="10",
            )