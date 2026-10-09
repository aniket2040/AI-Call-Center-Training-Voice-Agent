from __future__ import annotations

from livekit.agents import AgentSession, inference

from backend.app.config import settings


def create_voice_session() -> AgentSession:
    """Create the configured realtime voice pipeline."""

    return AgentSession(
        stt=inference.STT(
            model=settings.stt_model,
            language=settings.stt_language,
            api_key=settings.livekit_api_key,
            api_secret=settings.livekit_api_secret,
        ),
        llm=inference.LLM(
            model=settings.llm_model,
            api_key=settings.livekit_api_key,
            api_secret=settings.livekit_api_secret,
        ),
        tts=inference.TTS(
            model=settings.tts_model,
            voice=settings.tts_voice,
            language=settings.tts_language,
            api_key=settings.livekit_api_key,
            api_secret=settings.livekit_api_secret,
        ),
        turn_handling={
            "endpointing": {
                "mode": "fixed",
                "min_delay": settings.turn_min_endpointing_delay,
                "max_delay": settings.turn_max_endpointing_delay,
            },
            "interruption": {
                "enabled": settings.turn_interruption_enabled,
            },
        },
    )