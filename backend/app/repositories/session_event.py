
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.agents.state.events import SessionEventType
from backend.app.models import SessionEvent


class SessionEventRepository:
    """Append-only repository for creating and reading session events."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, event_id: int) -> SessionEvent | None:
        result = await self.session.execute(
            select(SessionEvent).where(SessionEvent.id == event_id)
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
            .order_by(
                SessionEvent.event_timestamp,
                SessionEvent.id,
            )
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def create(
        self,
        *,
        session_id: int,
        event_type: SessionEventType | str,
        event_timestamp: datetime | None = None,
        payload: dict[str, Any] | None = None,
    ) -> SessionEvent:
        validated_type = SessionEventType(event_type)
        timestamp = event_timestamp or datetime.now(timezone.utc)

        if timestamp.tzinfo is None or timestamp.utcoffset() is None:
            raise ValueError(
                "event_timestamp must include timezone information"
            )

        event = SessionEvent(
            session_id=session_id,
            event_type=validated_type.value,
            event_timestamp=timestamp,
            payload=payload if payload is not None else {},
        )

        self.session.add(event)
        await self.session.flush()
        return event