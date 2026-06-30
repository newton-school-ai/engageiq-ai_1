"""User model."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.config.settings import PrivacyMode, UserRole
from src.models.base import Base

if TYPE_CHECKING:
    from src.models.course import Course
    from src.models.engagement_log import EngagementLog
    from src.models.nudge import Nudge
    from src.models.report import Report


class User(Base):
    """Application user with role and privacy preferences."""

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(
            UserRole,
            name="user_role",
            native_enum=False,
            values_callable=lambda enum_class: [item.value for item in enum_class],
        ),
        nullable=False,
    )
    privacy_mode: Mapped[PrivacyMode] = mapped_column(
        Enum(
            PrivacyMode,
            name="privacy_mode",
            native_enum=False,
            values_callable=lambda enum_class: [item.value for item in enum_class],
        ),
        default=PrivacyMode.LOCAL_ONLY,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    taught_courses: Mapped[list[Course]] = relationship(
        back_populates="teacher",
        cascade="all, delete-orphan",
    )
    engagement_logs: Mapped[list[EngagementLog]] = relationship(
        back_populates="student",
        cascade="all, delete-orphan",
        foreign_keys="EngagementLog.student_id",
    )
    nudges: Mapped[list[Nudge]] = relationship(
        back_populates="student",
        cascade="all, delete-orphan",
        foreign_keys="Nudge.student_id",
    )
    reports: Mapped[list[Report]] = relationship(
        back_populates="generator",
        cascade="all, delete-orphan",
        foreign_keys="Report.generated_by",
    )
