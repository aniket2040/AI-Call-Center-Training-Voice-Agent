
import json

from livekit import api

from backend.app.config import settings


AGENT_NAME = "call-center-training-agent"


class LiveKitDispatchError(Exception):
    """Raised when an agent dispatch cannot be created."""


class LiveKitDispatchService:
    """Handles explicit dispatch of training agents to LiveKit rooms."""

    async def dispatch_agent(
        self,
        *,
        room_name: str,
        session_id: int,
        scenario_id: int,
        trainee_id: int,
        call_id: str,
    ) -> str:
        if not settings.livekit_url:
            raise LiveKitDispatchError("LiveKit URL is not configured.")

        if not settings.livekit_api_key or not settings.livekit_api_secret:
            raise LiveKitDispatchError(
                "LiveKit API credentials are not configured."
            )

        metadata = {
            "session_id": session_id,
            "scenario_id": scenario_id,
            "trainee_id": trainee_id,
            "call_id": call_id,
        }

        try:
            async with api.LiveKitAPI(
                url=settings.livekit_url,
                api_key=settings.livekit_api_key,
                api_secret=settings.livekit_api_secret,
            ) as livekit_api:
                dispatch = await livekit_api.agent_dispatch.create_dispatch(
                    api.CreateAgentDispatchRequest(
                        agent_name=AGENT_NAME,
                        room=room_name,
                        metadata=json.dumps(metadata),
                    )
                )

            return dispatch.id

        except Exception as exc:
            raise LiveKitDispatchError(
                f"Failed to dispatch training agent: {exc}"
            ) from exc
