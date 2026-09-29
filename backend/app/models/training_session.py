from __future__ import annotations
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base


class TrainingSession(Base):
    __tablename__ = "training_sessions"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    trainee_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    scenario_id: Mapped[int] = mapped_column(
        ForeignKey("scenarios.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    livekit_room_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )

    livekit_participant_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    phone_number: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="created",
        index=True,
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    recording_path: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    transcript_path: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    failure_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    trainee: Mapped["User"] = relationship(
        back_populates="training_sessions",
    )

    scenario: Mapped["Scenario"] = relationship(
        back_populates="training_sessions",
    )

    events: Mapped[list["SessionEvent"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )

    evaluation: Mapped["Evaluation | None"] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        uselist=False,
    )