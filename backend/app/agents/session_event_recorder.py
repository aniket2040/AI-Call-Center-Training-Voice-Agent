
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any

from backend.app.agents.state.events import SessionEventType
from backend.app.core.logging import get_logger
from backend.app.db.session import AsyncSessionFactory
from backend.app.repositories.session_event import SessionEventRepository

logger = get_logger("session_event_recorder")


class SessionEventRecorder:
    """Persist append-only training session events asynchronously."""

    def __init__(self, session_id: int) -> None:
        self.session_id = session_id
        self._tasks: set[asyncio.Task[None]] = set()

    def record(
        self,
        event_type: SessionEventType,
        payload: dict[str, Any] | None = None,
    ) -> None:
        """Schedule persistence from a running asyncio event loop."""
        try:
            task = asyncio.get_running_loop().create_task(
                self._persist(
                    event_type=event_type,
                    payload=payload or {},
                )
            )
        except RuntimeError:
            logger.error(
                "session_event_schedule_failed",
                session_id=self.session_id,
                event_type=event_type.value,
                reason="no_running_event_loop",
            )
            return

        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

    async def _persist(
        self,
        *,
        event_type: SessionEventType,
        payload: dict[str, Any],
    ) -> None:
        try:
            async with AsyncSessionFactory() as db:
                repository = SessionEventRepository(db)
                await repository.create(
                    session_id=self.session_id,
                    event_type=event_type,
                    event_timestamp=datetime.now(timezone.utc),
                    payload=payload,
                )
                await db.commit()
        except Exception:
            logger.exception(
                "session_event_persistence_failed",
                session_id=self.session_id,
                event_type=event_type.value,
            )

    async def drain(self) -> None:
        """Wait for currently scheduled writes to finish."""
        while self._tasks:
            await asyncio.gather(
                *tuple(self._tasks),
                return_exceptions=True
            )
