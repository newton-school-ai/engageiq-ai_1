"""User model — students and teachers."""

import enum
from typing import TYPE_CHECKING, List

from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.models.course import Course
    from src.models.engagement_log import EngagementLog
    from src.models.nudge import Nudge


class UserRole(str, enum.Enum):
    STUDENT = "student"
    TEACHER = "teacher"


class PrivacyMode(str, enum.Enum):
    LOCAL_ONLY = "local_only"
    SHARE_WITH_TEACHER = "share_with_teacher"


class User(TimestampMixin, Base):
    """Represents a student or teacher in the system."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="userrole"), nullable=False, default=UserRole.STUDENT
    )
    privacy_mode: Mapped[PrivacyMode] = mapped_column(
        Enum(PrivacyMode, name="privacymode"),
        nullable=False,
        default=PrivacyMode.LOCAL_ONLY,
    )

    # Relationships
    courses_taught: Mapped[List["Course"]] = relationship(
        "Course", back_populates="teacher", foreign_keys="Course.teacher_id"
    )
    engagement_logs: Mapped[List["EngagementLog"]] = relationship(
        "EngagementLog", back_populates="user"
    )
    nudges: Mapped[List["Nudge"]] = relationship("Nudge", back_populates="user")

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r} role={self.role}>"
