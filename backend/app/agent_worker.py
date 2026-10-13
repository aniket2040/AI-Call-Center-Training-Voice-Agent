
from __future__ import annotations

import json

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

        register_session_events(session)
        register_transcript_events(session, customer)
        register_tool_execution_events(session)

        await session.start(
            room=ctx.room,
            agent=customer,
        )

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

    except Exception:
        logger.exception(
            "agent_job_failed",
            room_name=room_name,
        )
        raise

    finally:
        logger.info("agent_job_finished", room_name=room_name)


if __name__ == "__main__":
    logger.info("agent_worker_starting", agent_name=AGENT_NAME)
    agents.cli.run_app(server)
