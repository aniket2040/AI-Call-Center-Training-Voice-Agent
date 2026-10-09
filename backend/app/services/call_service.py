
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.lifecycle.service import SessionLifecycleService
from backend.app.models.enums import TrainingSessionStatus
from backend.app.repositories.scenario import ScenarioRepository
from backend.app.repositories.session_event import SessionEventRepository
from backend.app.repositories.training_session import TrainingSessionRepository
from backend.app.repositories.user import UserRepository
from backend.app.services.livekit_dispatch import (
    LiveKitDispatchError,
    LiveKitDispatchService,
)


class CallServiceError(Exception):
    """Base exception for call-service errors."""


class TraineeNotFoundError(CallServiceError):
    """Raised when the requested trainee does not exist."""


class InvalidTraineeError(CallServiceError):
    """Raised when the requested user is not a trainee."""


class ScenarioNotFoundError(CallServiceError):
    """Raised when the requested scenario does not exist."""


class InactiveScenarioError(CallServiceError):
    """Raised when the requested scenario is inactive."""


class CallDispatchError(CallServiceError):
    """Raised when a training agent cannot be dispatched."""


class CallService:
    """Coordinates training-session creation and agent dispatch."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.users = UserRepository(db)
        self.scenarios = ScenarioRepository(db)
        self.sessions = TrainingSessionRepository(db)
        self.lifecycle = SessionLifecycleService(db)
        self.events = SessionEventRepository(db)
        self.dispatcher = LiveKitDispatchService()

    async def create_call(
        self,
        *,
        trainee_id: int,
        scenario_id: int,
        phone_number: str,
    ):
        trainee = await self.users.get_by_id(trainee_id)

        if trainee is None:
            raise TraineeNotFoundError(
                f"Trainee {trainee_id} was not found."
            )

        if trainee.role != "trainee":
            raise InvalidTraineeError(
                f"User {trainee_id} is not a trainee."
            )

        scenario = await self.scenarios.get_by_id(scenario_id)

        if scenario is None:
            raise ScenarioNotFoundError(
                f"Scenario {scenario_id} was not found."
            )

        if not scenario.is_active:
            raise InactiveScenarioError(
                f"Scenario {scenario_id} is inactive."
            )

        room_name = f"training-{uuid4().hex}"

        training_session = await self.sessions.create(
            trainee_id=trainee_id,
            scenario_id=scenario_id,
            livekit_room_name=room_name,
            phone_number=phone_number,
            status=TrainingSessionStatus.CREATED.value,
        )

        await self.db.commit()
        await self.db.refresh(training_session)

        try:
            await self.lifecycle.transition(
                training_session.id,
                TrainingSessionStatus.DISPATCHING,
                reason="Agent dispatch requested.",
            )
            await self.db.commit()

        except Exception:
            await self.db.rollback()
            raise

        try:
            dispatch_id = await self.dispatcher.dispatch_agent(
                room_name=room_name,
                session_id=training_session.id,
                scenario_id=training_session.scenario_id,
                trainee_id=training_session.trainee_id,
                call_id=str(training_session.id),
            )

        except LiveKitDispatchError as exc:
            try:
                await self.lifecycle.transition(
                    training_session.id,
                    TrainingSessionStatus.FAILED,
                    reason=f"Agent dispatch failed: {exc}",
                )
                await self.db.commit()
            except Exception:
                await self.db.rollback()
                raise

            raise CallDispatchError(
                "Unable to dispatch the training agent."
            ) from exc

        try:
            await self.events.create(
                session_id=training_session.id,
                event_type="agent_dispatched",
                event_timestamp=datetime.now(timezone.utc),
                payload={
                    "dispatch_id": dispatch_id,
                    "agent_name": "call-center-training-agent",
                    "room_name": room_name,
                },
            )

            await self.db.commit()
            await self.db.refresh(training_session)

        except Exception:
            await self.db.rollback()
            raise

        return training_session