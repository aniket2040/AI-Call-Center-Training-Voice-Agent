
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.lifecycle.transitions import validate_transition
from backend.app.models import TrainingSession
from backend.app.models.enums import TrainingSessionStatus
from backend.app.repositories.session_event import SessionEventRepository


class SessionNotFoundError(LookupError):
    """Raised when a training session does not exist."""


class SessionLifecycleService:
    """Manages persisted training-session lifecycle transitions."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.events = SessionEventRepository(db)

    async def transition(
        self,
        session_id: int,
        target: TrainingSessionStatus,
        *,
        reason: str | None = None,
    ) -> TrainingSession:

        result = await self.db.execute(
            select(TrainingSession)
            .where(TrainingSession.id == session_id)
            .with_for_update()
        )

        training_session = result.scalar_one_or_none()

        if training_session is None:
            raise SessionNotFoundError(
                f"Training session {session_id} was not found."
            )

        current = TrainingSessionStatus(training_session.status)

        should_transition = validate_transition(current, target)

        # Repeated requests must not create duplicate events.
        if not should_transition:
            return training_session

        now = datetime.now(timezone.utc)

        training_session.status = target.value
        training_session.updated_at = now

        if target == TrainingSessionStatus.ACTIVE:
            if training_session.started_at is None:
                training_session.started_at = now

        terminal_states = {
            TrainingSessionStatus.COMPLETED,
            TrainingSessionStatus.FAILED,
            TrainingSessionStatus.CANCELLED,
            TrainingSessionStatus.TIMEOUT,
        }

        if target in terminal_states:
            if training_session.ended_at is None:
                training_session.ended_at = now

        if target in {
            TrainingSessionStatus.FAILED,
            TrainingSessionStatus.CANCELLED,
            TrainingSessionStatus.TIMEOUT,
        }:
            training_session.failure_reason = reason

        await self.events.create(
            session_id=session_id,
            event_type="lifecycle_transition",
            event_timestamp=now,
            payload={
                "from_status": current.value,
                "to_status": target.value,
                "reason": reason,
            },
        )

        await self.db.flush()

        return training_session
