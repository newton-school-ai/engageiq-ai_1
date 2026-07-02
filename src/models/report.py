"""Report model — generated session and weekly engagement summaries."""

import enum
from typing import TYPE_CHECKING, Any, Dict, Optional

from sqlalchemy import Enum, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.models.session import Session


class ReportType(str, enum.Enum):
    SESSION_SUMMARY = "session_summary"
    WEEKLY_TREND = "weekly_trend"
    INTERVENTION_SUGGESTIONS = "intervention_suggestions"
    AT_RISK_STUDENTS = "at_risk_students"


class Report(TimestampMixin, Base):
    """Stores generated engagement reports for sessions."""

    __tablename__ = "reports"

    __table_args__ = (Index("ix_reports_session_id", "session_id"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False
    )
    report_type: Mapped[ReportType] = mapped_column(
        Enum(ReportType, name="reporttype"), nullable=False
    )

    # Full report data stored as JSONB for flexible querying
    content_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)

    # Optional rendered HTML/PDF path for download
    rendered_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    session: Mapped["Session"] = relationship("Session", back_populates="reports")

    def __repr__(self) -> str:
        return (
            f"<Report id={self.id} session={self.session_id} type={self.report_type}>"
        )
