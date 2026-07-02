"""Session model — one lecture/class session."""

import enum
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.models.course import Course
    from src.models.engagement_log import EngagementLog
    from src.models.nudge import Nudge
    from src.models.report import Report


class SessionStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Session(TimestampMixin, Base):
    """Represents a single lecture/class session."""

    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    end_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[SessionStatus] = mapped_column(
        Enum(SessionStatus, name="sessionstatus"),
        nullable=False,
        default=SessionStatus.SCHEDULED,
    )

    # Relationships
    course: Mapped["Course"] = relationship("Course", back_populates="sessions")
    engagement_logs: Mapped[List["EngagementLog"]] = relationship(
        "EngagementLog", back_populates="session"
    )
    nudges: Mapped[List["Nudge"]] = relationship("Nudge", back_populates="session")
    reports: Mapped[List["Report"]] = relationship("Report", back_populates="session")

    def __repr__(self) -> str:
        return f"<Session id={self.id} course_id={self.course_id} status={self.status}>"
