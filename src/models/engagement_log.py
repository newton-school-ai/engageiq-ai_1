"""Engagement log model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.session import Session
    from src.models.user import User


class EngagementLog(Base):
    """Per-frame student engagement signal captured during a session."""

    __tablename__ = "engagement_logs"
    __table_args__ = (
        CheckConstraint(
            "engagement_score >= 0 AND engagement_score <= 1",
            name="ck_engagement_logs_engagement_score_range",
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column(
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    student_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    frame_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    engagement_score: Mapped[float] = mapped_column(Float, nullable=False)
    engagement_state: Mapped[str] = mapped_column(String(50), nullable=False)
    gaze_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    drowsiness_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    expression: Mapped[str | None] = mapped_column(String(50), nullable=True)
    raw_data: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    session: Mapped[Session] = relationship(back_populates="engagement_logs")
    student: Mapped[User] = relationship(
        back_populates="engagement_logs",
        foreign_keys=[student_id],
    )
