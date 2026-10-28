
from __future__ import annotations

import json
from backend.app.agents.session_event_recorder import SessionEventRecorder
from backend.app.agents.state.events import SessionEventType
from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentServer, JobContext

from backend.app.agents.dispatch_metadata import (
    InvalidDispatchMetadataError,
    parse_dispatch_metadata,
)
from backend.app.agents.session_loader import (
    AgentSessionValidationError,
    build_training_scenario,
    load_agent_session,
)
from backend.app.agents.training_customer import (
    TrainingCustomer,
    create_training_session,
    register_session_events,
    register_transcript_events, register_tool_execution_events,
)
from backend.app.config import settings
from backend.app.core.logging import configure_logging, get_logger
from backend.app.db.session import AsyncSessionFactory

load_dotenv()
configure_logging()

logger = get_logger("agent_worker")

AGENT_NAME = "call-center-training-agent"

server = AgentServer(
    ws_url=settings.livekit_url,
    api_key=settings.livekit_api_key,
    api_secret=settings.livekit_api_secret,
    log_level=settings.log_level.lower(),
)


@server.rtc_session(agent_name=AGENT_NAME)
async def training_agent(ctx: JobContext) -> None:
    room_name = ctx.room.name

    logger.info("agent_job_started", room_name=room_name)
    event_recorder: SessionEventRecorder | None = None

    try:
        raw_metadata = ctx.job.metadata
        metadata = parse_dispatch_metadata(raw_metadata)

        async with AsyncSessionFactory() as db:
            training_session, db_scenario = await load_agent_session(
                db,
                metadata,
                room_name=room_name,
            )

            scenario = build_training_scenario(db_scenario)

        logger.info(
            "agent_session_validated",
            room_name=room_name,
            session_id=training_session.id,
            scenario_id=scenario.scenario_id,
            trainee_id=training_session.trainee_id,
            call_id=metadata.call_id,
        )

        session = create_training_session()
        customer = TrainingCustomer(scenario)

        event_recorder = SessionEventRecorder(training_session.id)

        async def drain_session_events() -> None:
            await event_recorder.drain()

        ctx.add_shutdown_callback(drain_session_events)

        event_recorder.record(
            SessionEventType.CALL_INITIATED,
            {
                "room_name": room_name,
                "scenario_id": training_session.scenario_id,
            },
        )

        register_session_events(session, event_recorder)
        register_transcript_events(session, customer, event_recorder)
        register_tool_execution_events(session, event_recorder)

        recorded_participant_sids: set[str] = set()

        def record_participant_joined(participant) -> None:
            if participant.sid in recorded_participant_sids:
                return

            recorded_participant_sids.add(participant.sid)

            event_recorder.record(
                SessionEventType.PARTICIPANT_JOINED,
                {
                    "identity": participant.identity,
                    "sid": participant.sid,
                    "room_name": room_name,
                },
            )

        @ctx.room.on("participant_connected")
        def on_participant_connected(participant) -> None:
            record_participant_joined(participant)

        await session.start(
            room=ctx.room,
            agent=customer,
        )
        for participant in ctx.room.remote_participants.values():
            record_participant_joined(participant)

        logger.info(
            "agent_session_started",
            room_name=room_name,
            session_id=training_session.id,
            scenario_id=scenario.scenario_id,
        )

    except (
        InvalidDispatchMetadataError,
        AgentSessionValidationError,
    ):
        logger.exception(
            "agent_job_validation_failed",
            room_name=room_name,
        )
        raise



    except Exception as exc:

        logger.exception(

            "agent_job_failed",

            room_name=room_name,

        )

        if event_recorder is not None:
            event_recorder.record(

                SessionEventType.SESSION_FAILED,

                {

                    "stage": "agent_runtime",

                    "error_type": type(exc).__name__,

                    "reason": str(exc),

                    "room_name": room_name,

                },

            )

            await event_recorder.drain()

        raise

    finally:
        logger.info("agent_job_finished", room_name=room_name)


if __name__ == "__main__":
    logger.info("agent_worker_starting", agent_name=AGENT_NAME)
    agents.cli.run_app(server)
