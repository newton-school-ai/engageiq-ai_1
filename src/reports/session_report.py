"""Build HTML engagement summaries for lecture sessions."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy import select
from sqlalchemy.orm import Session as DatabaseSession

from src.database import SessionLocal
from src.models.course import Course
from src.models.engagement_log import EngagementLog
from src.models.session import Session


class SessionReportGenerator:
    """Generate a self-contained HTML engagement report for one session."""

    def __init__(self, db: DatabaseSession | None = None) -> None:
        """Create a generator, optionally using an existing database session."""
        self.db = db

    def build_report_data(self, session_id: int) -> dict[str, Any]:
        """Load and aggregate session data for the report template."""
        owns_db = self.db is None
        db = self.db or SessionLocal()
        try:
            lecture = db.get(Session, session_id)
            if lecture is None:
                raise ValueError(f"Session {session_id} was not found")

            course = db.get(Course, lecture.course_id)
            logs = db.execute(
                select(
                    EngagementLog.timestamp,
                    EngagementLog.user_id,
                    EngagementLog.score,
                    EngagementLog.state,
                )
                .where(EngagementLog.session_id == session_id)
                .order_by(EngagementLog.timestamp, EngagementLog.id)
                .execution_options(yield_per=5000)
            )
            return self._aggregate(lecture, course, logs)
        finally:
            if owns_db:
                db.close()

    def generate(self, session_id: int, output: str | Path | None = None) -> str:
        """Render the session report HTML and optionally save it to a file."""
        report_data = self.build_report_data(session_id)
        template_dir = Path(__file__).resolve().parents[1] / "templates"
        environment = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(["html", "xml"]),
        )
        html = environment.get_template("session_report.html").render(**report_data)
        if output is not None:
            Path(output).write_text(html, encoding="utf-8")
        return html

    @staticmethod
    def _aggregate(
        lecture: Session,
        course: Course | None,
        logs: Iterable[tuple[datetime, int, float, Any]],
    ) -> dict[str, Any]:
        """Summarize log records without exposing student names or identifiers."""
        session_start = lecture.start_time
        buckets: dict[datetime, list[float | int]] = {}
        student_totals: dict[int, list[float | int]] = {}
        state_counts: Counter[str] = Counter()
        last_timestamp: datetime | None = None
        total_score = 0.0
        log_count = 0
        for timestamp, user_id, raw_score, raw_state in logs:
            score = float(raw_score)
            minute = timestamp.replace(second=0, microsecond=0)
            bucket = buckets.setdefault(minute, [0.0, 0])
            bucket[0] += score
            bucket[1] += 1
            student_total = student_totals.setdefault(user_id, [0.0, 0])
            student_total[0] += score
            student_total[1] += 1
            state = getattr(raw_state, "value", str(raw_state))
            state_counts[state] += 1
            total_score += score
            log_count += 1
            last_timestamp = timestamp

        timeline = [
            {
                "timestamp": minute.isoformat(sep=" ", timespec="minutes"),
                "elapsed_minutes": max(
                    0, int((minute - session_start).total_seconds() // 60)
                ),
                "engagement": round(scores[0] / scores[1], 2),
            }
            for minute, scores in sorted(buckets.items())
        ]
        dips = sorted(
            timeline, key=lambda point: (point["engagement"], point["timestamp"])
        )[:3]
        class_average = total_score / log_count if log_count else 0.0
        student_labels = {
            student_id: f"Student {index + 1}"
            for index, student_id in enumerate(sorted(student_totals))
        }
        comparison = [
            {
                "label": student_labels[student_id],
                "average": round(totals[0] / totals[1], 2),
                "class_average": round(class_average, 2),
            }
            for student_id, totals in sorted(student_totals.items())
            if totals[1]
        ]

        end_time = lecture.end_time or last_timestamp
        duration_minutes = (
            max(0, int((end_time - session_start).total_seconds() // 60))
            if end_time is not None
            else 0
        )
        return {
            "session": {
                "id": lecture.id,
                "course_name": course.name if course else f"Course {lecture.course_id}",
                "course_code": course.code if course else "",
                "start_time": session_start.isoformat(sep=" ", timespec="minutes"),
                "end_time": (
                    end_time.isoformat(sep=" ", timespec="minutes")
                    if end_time
                    else "In progress"
                ),
                "duration_minutes": duration_minutes,
                "student_count": len(student_totals),
                "log_count": log_count,
            },
            "class_average": round(class_average, 2),
            "timeline": timeline,
            "state_distribution": [
                {"state": state.replace("_", " ").title(), "count": count}
                for state, count in sorted(state_counts.items())
            ],
            "distraction_moments": [
                {**point, "timestamp": point["timestamp"]} for point in dips
            ],
            "student_comparison": comparison,
        }


def main() -> None:
    """Run the report generator from the command line."""
    parser = argparse.ArgumentParser(description="Generate a session engagement report")
    parser.add_argument("--session-id", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    SessionReportGenerator().generate(args.session_id, args.output)
    print(f"Session report written to {args.output}")


if __name__ == "__main__":
    main()
