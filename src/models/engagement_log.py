"""EngagementLog model — per-frame engagement score storage."""

import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.models.session import Session
    from src.models.user import User


class EngagementState(str, enum.Enum):
    ENGAGED = "engaged"
    PASSIVE = "passive"
    DISTRACTED = "distracted"
    DROWSY = "drowsy"
    CONFUSED = "confused"


class EngagementLog(TimestampMixin, Base):
    """Stores per-frame engagement signals for a student in a session."""

    __tablename__ = "engagement_logs"

    __table_args__ = (
        # Composite index for the most common query: all logs for a student in a session
        Index("ix_engagement_logs_session_user", "session_id", "user_id"),
        # Index for time-series queries within a session
        Index("ix_engagement_logs_session_timestamp", "session_id", "timestamp"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Composite engagement score (0–100)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    state: Mapped[EngagementState] = mapped_column(
        Enum(EngagementState, name="engagementstate"), nullable=False
    )

    # Raw CV signal scores (0–100 each, nullable if signal unavailable)
    gaze_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    pose_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    expression_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    alertness_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Boolean flags from detectors
    is_drowsy: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_yawning: Mapped[bool] = mapped_column(default=False, nullable=False)
    phone_detected: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Raw detector outputs
    gaze_direction: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    expression: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    head_pitch: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    head_yaw: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ear_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Frame metadata
    frame_index: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationships
    session: Mapped["Session"] = relationship(
        "Session", back_populates="engagement_logs"
    )
    user: Mapped["User"] = relationship("User", back_populates="engagement_logs")

    def __repr__(self) -> str:
        return (
            f"<EngagementLog id={self.id} session={self.session_id} "
            f"user={self.user_id} score={self.score:.1f} state={self.state}>"
        )
