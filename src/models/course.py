"""Course model — a subject taught by a teacher."""

from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.models.session import Session
    from src.models.user import User


class Course(TimestampMixin, Base):
    """Represents a course/subject taught by a teacher."""

    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(
        String(50), nullable=False, unique=True, index=True
    )
    teacher_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    # Relationships
    teacher: Mapped["User"] = relationship(
        "User", back_populates="courses_taught", foreign_keys=[teacher_id]
    )
    sessions: Mapped[List["Session"]] = relationship("Session", back_populates="course")

    def __repr__(self) -> str:
        return f"<Course id={self.id} code={self.code!r} name={self.name!r}>"
