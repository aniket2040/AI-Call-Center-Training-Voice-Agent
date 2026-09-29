from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models import TrainingSession


class TrainingSessionRepository:
    """Database operations for training sessions."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self,
        session_id: int,
    ) -> TrainingSession | None:
        result = await self.session.execute(
            select(TrainingSession).where(
                TrainingSession.id == session_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_room_name(
        self,
        room_name: str,
    ) -> TrainingSession | None:
        result = await self.session.execute(
            select(TrainingSession).where(
                TrainingSession.livekit_room_name == room_name
            )
        )
        return result.scalar_one_or_none()

    async def list_by_trainee(
        self,
        trainee_id: int,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[TrainingSession]:
        result = await self.session.execute(
            select(TrainingSession)
            .where(TrainingSession.trainee_id == trainee_id)
            .order_by(TrainingSession.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def create(
        self,
        *,
        trainee_id: int,
        scenario_id: int,
        livekit_room_name: str,
        livekit_participant_id: str | None = None,
        phone_number: str | None = None,
        status: str = "created",
    ) -> TrainingSession:
        training_session = TrainingSession(
            trainee_id=trainee_id,
            scenario_id=scenario_id,
            livekit_room_name=livekit_room_name,
            livekit_participant_id=livekit_participant_id,
            phone_number=phone_number,
            status=status,
        )

        self.session.add(training_session)
        await self.session.flush()

        return training_session

    async def update_status(
        self,
        training_session: TrainingSession,
        status: str,
    ) -> TrainingSession:
        training_session.status = status

        await self.session.flush()

        return training_session