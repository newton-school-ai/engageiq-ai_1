"""Nudge model — records nudges sent to students and their effectiveness."""

import enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Enum, Float, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.models.session import Session
    from src.models.user import User


class NudgeType(str, enum.Enum):
    FOCUS_REMINDER = "focus_reminder"
    BREAK_SUGGESTION = "break_suggestion"
    TOPIC_REVIEW = "topic_review"
    ENCOURAGEMENT = "encouragement"
    DROWSINESS_ALERT = "drowsiness_alert"


class Nudge(TimestampMixin, Base):
    """Records a nudge sent to a student and tracks its effectiveness."""

    __tablename__ = "nudges"

    __table_args__ = (
        # Most common query: all nudges for a session
        Index("ix_nudges_session_id", "session_id"),
        # Lookup nudges for a specific student in a session
        Index("ix_nudges_session_user", "session_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    nudge_type: Mapped[NudgeType] = mapped_column(
        Enum(NudgeType, name="nudgetype"), nullable=False
    )

    # What state triggered the nudge
    trigger_state: Mapped[str] = mapped_column(String(50), nullable=False)

    # Engagement score at time of nudge
    pre_nudge_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Engagement score delta measured after the cooldown window
    # Positive = nudge improved engagement, negative = no effect
    effectiveness_delta: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # The actual message delivered to the student
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Whether the student acknowledged the nudge
    acknowledged: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Relationships
    session: Mapped["Session"] = relationship("Session", back_populates="nudges")
    user: Mapped["User"] = relationship("User", back_populates="nudges")

    def __repr__(self) -> str:
        return (
            f"<Nudge id={self.id} session={self.session_id} "
            f"user={self.user_id} type={self.nudge_type}>"
        )
