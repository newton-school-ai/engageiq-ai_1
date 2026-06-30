"""Session model."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.course import Course
    from src.models.engagement_log import EngagementLog
    from src.models.nudge import Nudge
    from src.models.report import Report


class SessionStatus(str, Enum):
    """Lifecycle state for a lecture session."""

    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"


class Session(Base):
    """Lecture session attached to a course."""

    __tablename__ = "sessions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    course_id: Mapped[UUID] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    status: Mapped[SessionStatus] = mapped_column(
        SqlEnum(
            SessionStatus,
            name="session_status",
            native_enum=False,
            values_callable=lambda enum_class: [item.value for item in enum_class],
        ),
        default=SessionStatus.PENDING,
        nullable=False,
    )

    course: Mapped[Course] = relationship(back_populates="sessions")
    engagement_logs: Mapped[list[EngagementLog]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )
    nudges: Mapped[list[Nudge]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )
    reports: Mapped[list[Report]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )
