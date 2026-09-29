from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models import SessionEvent


class SessionEventRepository:
    """Database operations for training-session events."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self,
        event_id: int,
    ) -> SessionEvent | None:
        result = await self.session.execute(
            select(SessionEvent).where(
                SessionEvent.id == event_id
            )
        )
        return result.scalar_one_or_none()

    async def list_by_session(
        self,
        session_id: int,
        *,
        limit: int = 500,
        offset: int = 0,
    ) -> list[SessionEvent]:
        result = await self.session.execute(
            select(SessionEvent)
            .where(SessionEvent.session_id == session_id)
            .order_by(SessionEvent.event_timestamp)
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def create(
        self,
        *,
        session_id: int,
        event_type: str,
        event_timestamp: datetime,
        payload: dict,
    ) -> SessionEvent:
        event = SessionEvent(
            session_id=session_id,
            event_type=event_type,
            event_timestamp=event_timestamp,
            payload=payload,
        )

        self.session.add(event)
        await self.session.flush()

        return event